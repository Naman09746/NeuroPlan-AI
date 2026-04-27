import React from 'react'
import Sidebar from './Sidebar'

const MainLayout = ({ children }) => {
  return (
    <div className="flex bg-slate-50 min-h-screen">
      {/* Sidebar - Fixed width */}
      <Sidebar />
      
      {/* Main Content - Flex-1 */}
      <main className="flex-1 overflow-y-auto max-h-screen">
        {children}
      </main>
    </div>
  )
}

export default MainLayout
