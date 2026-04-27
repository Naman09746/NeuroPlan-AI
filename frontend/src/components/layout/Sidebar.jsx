import React from 'react'
import { LayoutDashboard, BookOpen, Calendar, BarChart2, Settings, LogOut, Brain } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { clsx } from 'clsx'
import { useAuthStore } from '@/store/useAuthStore'

const SidebarItem = ({ icon: Icon, label, path, active }) => (
  <Link
    to={path}
    className={clsx(
      "nav-link animate-slide-up",
      active && "nav-link-active"
    )}
  >
    <Icon className={clsx("w-5 h-5", active ? "text-primary-600" : "text-surface-400 group-hover:text-primary-500")} />
    <span className="tracking-tight">{label}</span>
  </Link>
)

const Sidebar = () => {
  const location = useLocation()
  const { logout, user } = useAuthStore()
  
  return (
    <div className="w-72 h-screen glass-panel flex flex-col p-8 sticky top-0">
      <div className="flex items-center gap-4 mb-12 px-2 group cursor-pointer">
        <div className="w-12 h-12 bg-primary-600 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-200 group-hover:rotate-6 transition-transform duration-300">
          <Brain className="text-white w-7 h-7" />
        </div>
        <div>
          <h1 className="text-2xl font-black text-surface-900 tracking-tighter">
            NeuroPlan
          </h1>
          <div className="h-1 w-12 bg-primary-500 rounded-full"></div>
        </div>
      </div>

      <nav className="flex-1 space-y-3">
        <SidebarItem icon={LayoutDashboard} label="Dashboard" path="/" active={location.pathname === '/'} />
        <SidebarItem icon={BookOpen} label="Curriculum" path="/subjects" active={location.pathname === '/subjects'} />
        <SidebarItem icon={Calendar} label="Study Plan" path="/plan" active={location.pathname === '/plan'} />
        <SidebarItem icon={BarChart2} label="Analytics" path="/analytics" active={location.pathname === '/analytics'} />
      </nav>

      <div className="mt-auto pt-8 border-t border-white/20 space-y-3">
        <div className="flex items-center gap-3 px-4 py-3 mb-4">
           <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold border-2 border-white shadow-sm">
             {user?.name?.[0].toUpperCase() || 'U'}
           </div>
           <div className="overflow-hidden">
             <p className="text-sm font-bold text-surface-900 truncate">{user?.name || 'User Profile'}</p>
             <p className="text-[10px] font-bold text-primary-500 uppercase tracking-widest leading-none">Standard Mind</p>
           </div>
        </div>

        <SidebarItem icon={Settings} label="Settings" path="/settings" active={location.pathname === '/settings'} />
        <button 
          onClick={logout}
          className="flex items-center gap-3 px-4 py-3 rounded-2xl text-surface-400 hover:bg-red-50 hover:text-red-600 transition-all w-full font-medium"
        >
          <LogOut className="w-5 h-5" />
          <span className="tracking-tight">Sign Out</span>
        </button>
      </div>
    </div>
  )
}

export default Sidebar
