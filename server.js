const express = require('express');
const cors = require('cors');
const multer = require('multer');
const robot = require('robotjs');
const open = require('open'); // For /api/youtube/play/:videoId
const youtubedl = require('youtube-dl-exec'); // For /api/youtube/download
const fs = require('fs'); // For file system operations
const path = require('path'); // For path manipulation

const app = express();
const port = 3001;

// File type extensions
const VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.webm'];
const AUDIO_EXTENSIONS = ['.mp3', '.wav', '.aac', '.ogg', '.flac'];
const PRESENTATION_EXTENSIONS = ['.ppt', '.pptx', '.odp', '.key', '.pdf'];
const IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'];
const ALLOWED_EXTENSIONS = [
  ...VIDEO_EXTENSIONS,
  ...AUDIO_EXTENSIONS,
  ...PRESENTATION_EXTENSIONS,
  ...IMAGE_EXTENSIONS,
];

const UPLOAD_PASSWORD = 'password123'; // Hardcoded password

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true })); // For form data
app.use('/files', express.static(path.join(__dirname, 'files'))); // Serve downloaded files

// Create 'files' directory if it doesn't exist
const filesDir = path.join(__dirname, 'files');
if (!fs.existsSync(filesDir)) {
  fs.mkdirSync(filesDir, { recursive: true });
}

// Multer setup for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const category = req.body.category || 'general';
    const categoryDir = path.join(filesDir, category);
    if (!fs.existsSync(categoryDir)) {
      fs.mkdirSync(categoryDir, { recursive: true });
    }
    cb(null, categoryDir);
  },
  filename: function (req, file, cb) {
    cb(null, file.originalname);
  },
});

const upload = multer({
  storage: storage,
  fileFilter: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return cb(new Error('File type not allowed'), false);
    }
    cb(null, true);
  },
});


// Helper function to determine file type
function getFileType(filename) {
  const ext = path.extname(filename).toLowerCase();
  if (VIDEO_EXTENSIONS.includes(ext)) return 'video';
  if (AUDIO_EXTENSIONS.includes(ext)) return 'audio';
  if (PRESENTATION_EXTENSIONS.includes(ext)) return 'presentation';
  if (IMAGE_EXTENSIONS.includes(ext)) return 'image';
  return 'other';
}

// Recursive function to search files
function searchFilesRecursive(directory, term, results, rootDir) {
  const items = fs.readdirSync(directory);
  for (const item of items) {
    const itemPath = path.join(directory, item);
    const stat = fs.statSync(itemPath);
    if (stat.isDirectory()) {
      searchFilesRecursive(itemPath, term, results, rootDir);
    } else if (item.toLowerCase().includes(term.toLowerCase())) {
      results.push({
        name: item,
        path: path.relative(rootDir, itemPath),
        type: getFileType(item),
      });
    }
  }
}

// Simple GET route for testing
app.get('/', (req, res) => {
  res.send('Hello World!');
});

// File Management Routes
app.get('/api/files/search', (req, res) => {
  const { term } = req.query;
  if (!term) {
    return res.status(400).send({ message: 'Search term is required' });
  }
  try {
    const results = [];
    searchFilesRecursive(filesDir, term, results, filesDir);
    res.status(200).json(results);
  } catch (error) {
    console.error('Error searching files:', error);
    res.status(500).send({ message: 'Error searching files', error: error.message });
  }
});

app.post('/api/files/play', async (req, res) => {
  const { filePath, fileType } = req.body;

  if (!filePath || !fileType) {
    return res.status(400).send({ message: 'filePath and fileType are required' });
  }

  const absoluteFilePath = path.join(filesDir, filePath); // filesDir is the base /app/files directory

  if (!fs.existsSync(absoluteFilePath)) {
    return res.status(404).send({ message: 'File not found' });
  }

  console.log(`Attempting to play ${fileType} file: ${absoluteFilePath}`);

  try {
    if (fileType === 'video' || fileType === 'audio' || fileType === 'image') {
      await open(absoluteFilePath);
      res.status(200).send({ message: `Playing ${fileType}: ${path.basename(filePath)}` });
    } else if (fileType === 'presentation') {
      await open(absoluteFilePath);
      // For presentations (especially .ppt, .pptx), give time for app to open then press F5
      if (!filePath.endsWith('.pdf')) { // PDFs usually open in presentation mode by default or don't need F5
        setTimeout(() => {
          try {
            robot.keyTap('f5');
            console.log('Pressed F5 for presentation.');
          } catch (e) {
            console.error('Failed to press F5 for presentation:', e);
            // Cannot send response here as it might have already been sent
          }
        }, 3000); // 3-second delay
      }
      res.status(200).send({ message: `Opening presentation: ${path.basename(filePath)}` });
    } else {
      res.status(400).send({ message: `Unsupported file type: ${fileType}` });
    }
  } catch (error) {
    console.error(`Error playing file ${filePath}:`, error);
    res.status(500).send({ message: 'Error playing file', error: error.message });
  }
});

app.post('/api/files/upload', (req, res) => {
  // Password check middleware specifically for this route
  const passwordMiddleware = (req, res, next) => {
    const { password } = req.body;
    if (password !== UPLOAD_PASSWORD) {
      return res.status(401).send({ message: 'Incorrect password' });
    }
    next();
  };

  // Apply password check then multer upload
  passwordMiddleware(req, res, () => {
    upload.single('file')(req, res, function (err) {
      if (err instanceof multer.MulterError) {
        return res.status(400).send({ message: `Multer error: ${err.message}` });
      } else if (err) {
        // This will catch the 'File type not allowed' error
        return res.status(400).send({ message: err.message });
      }
      if (!req.file) {
        return res.status(400).send({ message: 'No file uploaded' });
      }
      res.status(200).send({
        message: 'File uploaded successfully',
        filename: req.file.filename,
        path: path.relative(filesDir, req.file.path),
        category: req.body.category || 'general',
      });
    });
  });
});

app.get('/api/files/doxologia/:category', (req, res) => {
  const { category } = req.params;
  const categoryDir = path.join(filesDir, category);

  if (!fs.existsSync(categoryDir)) {
    return res.status(404).send({ message: 'Category not found' });
  }

  try {
    const items = fs.readdirSync(categoryDir);
    const fileDetails = [];
    for (const item of items) {
      const itemPath = path.join(categoryDir, item);
      const stat = fs.statSync(itemPath);
      if (stat.isFile()) {
        fileDetails.push({
          name: item,
          path: path.join(category, item), // Path relative to filesDir
          type: getFileType(item),
        });
      }
    }
    res.status(200).json(fileDetails);
  } catch (error) {
    console.error(`Error listing files in category ${category}:`, error);
    res.status(500).send({ message: 'Error listing files', error: error.message });
  }
});


// Media control routes
app.post('/api/media/play', (req, res) => {
  try {
    robot.keyTap('space');
    res.status(200).send({ message: 'Play/Pause toggled' });
  } catch (error) {
    res.status(500).send({ message: 'Error toggling play/pause', error });
  }
});

app.post('/api/media/volume/:action', (req, res) => {
  const { action } = req.params;
  try {
    if (action === 'up') {
      robot.keyTap('audio_vol_up');
      res.status(200).send({ message: 'Volume increased' });
    } else if (action === 'down') {
      robot.keyTap('audio_vol_down');
      res.status(200).send({ message: 'Volume decreased' });
    } else {
      res.status(400).send({ message: 'Invalid volume action' });
    }
  } catch (error) {
    res.status(500).send({ message: 'Error adjusting volume', error });
  }
});

app.post('/api/media/volume/mute', (req, res) => {
  try {
    robot.keyTap('audio_mute');
    res.status(200).send({ message: 'Mute toggled' });
  } catch (error) {
    res.status(500).send({ message: 'Error toggling mute', error });
  }
});

app.post('/api/media/fullscreen', (req, res) => {
  try {
    robot.keyTap('f11');
    res.status(200).send({ message: 'Fullscreen toggled' });
  } catch (error) {
    res.status(500).send({ message: 'Error toggling fullscreen', error });
  }
});

app.post('/api/media/hide-controls', (req, res) => {
  try {
    const screenSize = robot.getScreenSize();
    robot.moveMouse(screenSize.width / 2, screenSize.height / 2);
    robot.mouseClick();
    res.status(200).send({ message: 'Controls hidden' });
  } catch (error) {
    res.status(500).send({ message: 'Error hiding controls', error });
  }
});

// Presentation control routes
app.post('/api/presentation/next', (req, res) => {
  try {
    robot.keyTap('right');
    res.status(200).send({ message: 'Next slide' });
  } catch (error) {
    res.status(500).send({ message: 'Error advancing to next slide', error });
  }
});

app.post('/api/presentation/previous', (req, res) => {
  try {
    robot.keyTap('left');
    res.status(200).send({ message: 'Previous slide' });
  } catch (error) {
    res.status(500).send({ message: 'Error going to previous slide', error });
  }
});

app.post('/api/presentation/fullscreen', (req, res) => {
  try {
    robot.keyTap('f5');
    res.status(200).send({ message: 'Presentation mode toggled' });
  } catch (error) {
    res.status(500).send({ message: 'Error toggling presentation mode', error });
  }
});

// System control routes
app.post('/api/system/close-app', (req, res) => {
  try {
    robot.keyTap('f4', 'alt');
    res.status(200).send({ message: 'Close app command sent' });
  } catch (error) {
    res.status(500).send({ message: 'Error sending close app command', error });
  }
});

app.post('/api/system/minimize', (req, res) => {
  try {
    robot.keyTap('d', 'super'); // 'super' is typically the Windows/Command key
    res.status(200).send({ message: 'Minimize command sent' });
  } catch (error) {
    res.status(500).send({ message: 'Error sending minimize command', error });
  }
});

app.post('/api/system/maximize', (req, res) => {
  try {
    robot.keyTap('up', 'super'); // 'super' is typically the Windows/Command key
    res.status(200).send({ message: 'Maximize command sent' });
  } catch (error) {
    res.status(500).send({ message: 'Error sending maximize command', error });
  }
});

app.post('/api/system/switch-app', (req, res) => {
  try {
    robot.keyTap('tab', 'alt');
    res.status(200).send({ message: 'Switch app command sent' });
  } catch (error) {
    res.status(500).send({ message: 'Error sending switch app command', error });
  }
});

app.post('/api/system/press-keys', (req, res) => {
  const { keys } = req.body;
  if (!keys || !Array.isArray(keys) || keys.length === 0) {
    return res.status(400).send({ message: 'Invalid keys array provided' });
  }
  try {
    const mainKey = keys[0];
    const modifiers = keys.slice(1);
    robot.keyTap(mainKey, modifiers.length > 0 ? modifiers : undefined);
    res.status(200).send({ message: `Keys pressed: ${keys.join('+')}` });
  } catch (error) {
    console.error('Error pressing keys:', error); // Log the detailed error
    res.status(500).send({ message: 'Error pressing keys', error: error.message });
  }
});

app.post('/api/system/click-center', (req, res) => {
  try {
    const screenSize = robot.getScreenSize();
    robot.moveMouse(screenSize.width / 2, screenSize.height / 2);
    robot.mouseClick();
    res.status(200).send({ message: 'Clicked center of the screen' });
  } catch (error) {
    res.status(500).send({ message: 'Error clicking center of the screen', error });
  }
});

app.post('/api/system/close-window', (req, res) => {
  try {
    robot.keyTap('f4', 'alt'); // Same as close-app for many systems
    res.status(200).send({ message: 'Close window command sent' });
  } catch (error) {
    res.status(500).send({ message: 'Error sending close window command', error });
  }
});

// YouTube control routes
app.get('/api/youtube/search', (req, res) => {
  res.status(200).send({ message: 'YouTube search to be implemented by the client or later on the server.' });
});

app.post('/api/youtube/play/:videoId', async (req, res) => {
  const { videoId } = req.params;
  const youtubeUrl = `https://www.youtube.com/watch?v=${videoId}`;
  try {
    await open(youtubeUrl);
    res.status(200).send({ message: `Attempting to play YouTube video: ${youtubeUrl}` });
  } catch (error) {
    console.error('Error opening YouTube URL:', error);
    res.status(500).send({ message: 'Error playing YouTube video', error: error.message });
  }
});

app.post('/api/youtube/fullscreen', (req, res) => {
  try {
    robot.keyTap('f');
    res.status(200).send({ message: 'YouTube fullscreen toggled' });
  } catch (error) {
    res.status(500).send({ message: 'Error toggling YouTube fullscreen', error });
  }
});

app.post('/api/youtube/rewind', (req, res) => {
  try {
    robot.keyTap('j');
    res.status(200).send({ message: 'YouTube rewind command sent' });
  } catch (error) {
    res.status(500).send({ message: 'Error sending YouTube rewind command', error });
  }
});

app.post('/api/youtube/download', async (req, res) => {
  const { url, category = 'general' } = req.body;
  if (!url) {
    return res.status(400).send({ message: 'URL is required' });
  }

  const categoryDir = path.join(filesDir, category);
  if (!fs.existsSync(categoryDir)) {
    fs.mkdirSync(categoryDir, { recursive: true });
  }

  try {
    res.status(202).send({ message: 'Download started. Check server logs for progress.' }); // Send initial acceptance

    console.log(`Starting download for ${url} into ${categoryDir}`);
    
    const promise = youtubedl(url, {
      output: path.join(categoryDir, '%(title)s.%(ext)s'),
      format: 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    });

    promise.then(output => {
      console.log('Download finished:', output);
    }).catch(err => {
      console.error('Error during download:', err);
    });

  } catch (error) {
    console.error('Error initiating download:', error);
    if (!res.headersSent) {
        res.status(500).send({ message: 'Error initiating download', error: error.message });
    }
  }
});

app.post('/api/youtube/press-key', (req, res) => {
  const { key } = req.body;
  if (!key) {
    return res.status(400).send({ message: 'Key is required' });
  }
  try {
    robot.keyTap(key);
    res.status(200).send({ message: `Key pressed: ${key}` });
  } catch (error) {
    console.error('Error pressing key for YouTube:', error);
    res.status(500).send({ message: 'Error pressing key', error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
