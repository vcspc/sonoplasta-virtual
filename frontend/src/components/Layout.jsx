import React from 'react';
import SideMenu from './SideMenu';
import { Outlet } from 'react-router-dom'; // Outlet is used to render child routes
import './Layout.css';

function Layout() {
  return (
    <div className="layout-container">
      <SideMenu />
      <div className="main-content">
        <Outlet /> {/* Child routes will be rendered here */}
      </div>
    </div>
  );
}

export default Layout;
