import React from 'react'
import { Settings as SettingsIcon, User, Bell, Lock, Shield, Moon, Globe, LogOut } from 'lucide-react'
import { useAuthStore } from '@/store/useAuthStore'
import { Button } from '@/components/ui/Button'
import apiClient from '../api/client'
import toast from 'react-hot-toast'
import { useState, useEffect } from 'react'
import { useConfigStore } from '@/store/useConfigStore'

const SettingsPage = () => {
    const { user, logout, fetchMe } = useAuthStore()
    const { aiHealth, fetchAIHealth } = useConfigStore()
    const [isUpdating, setIsUpdating] = useState(false)

    useEffect(() => {
        fetchAIHealth()
    }, [])

    const prefs = user?.preferences || {}

    const updatePreference = async (key, value) => {
        setIsUpdating(true)
        try {
            await apiClient.put('/users/me/preferences', { [key]: value })
            await fetchMe()
            toast.success('Preference synchronized')
        } catch (err) {
            toast.error('Failed to update preference')
        } finally {
            setIsUpdating(false)
        }
    }

    return (
        <div className="p-12 max-w-4xl mx-auto space-y-12 pb-20">
            <div>
                <h2 className="text-4xl font-black text-surface-900 tracking-tight">System Settings</h2>
                <p className="text-surface-400 mt-2 font-medium">Manage your neural profile and application preferences.</p>
            </div>

            <div className="space-y-6">
                {/* Profile Section */}
                <div className="glass-card p-8">
                    <div className="flex items-center gap-4 mb-8">
                        <div className="p-3 bg-primary-50 rounded-2xl">
                            <User className="w-6 h-6 text-primary-600" />
                        </div>
                        <h3 className="text-xl font-black text-surface-900">Personal Profile</h3>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-surface-400 uppercase tracking-widest pl-1">Full Name</label>
                            <div className="p-4 bg-surface-50 rounded-2xl border-2 border-white font-bold text-surface-900">
                                {user?.name}
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-surface-400 uppercase tracking-widest pl-1">Email Address</label>
                            <div className="p-4 bg-surface-50 rounded-2xl border-2 border-white font-bold text-surface-900">
                                {user?.email}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Preferences Section */}
                <div className="glass-card p-8">
                    <div className="flex items-center gap-4 mb-8">
                        <div className="p-3 bg-purple-50 rounded-2xl">
                            <Moon className="w-6 h-6 text-purple-600" />
                        </div>
                        <h3 className="text-xl font-black text-surface-900">Application Preferences</h3>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 hover:bg-surface-50 rounded-2xl transition-all border border-transparent hover:border-white">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm">
                                    <Bell className="w-5 h-5 text-surface-400" />
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-surface-900">Neural Notifications</p>
                                    <p className="text-xs text-surface-400">Receive alerts for scheduled assessment windows.</p>
                                </div>
                            </div>
                            <div className="w-12 h-6 bg-primary-600 rounded-full relative">
                                <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div>
                            </div>
                        </div>

                        <div className="flex items-center justify-between p-4 hover:bg-surface-50 rounded-2xl transition-all border border-transparent hover:border-white">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm">
                                    <Shield className="w-5 h-5 text-surface-400" />
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-surface-900">Privacy Mode</p>
                                    <p className="text-xs text-surface-400">Anonymize study statistics on the global leaderboard.</p>
                                </div>
                            </div>
                            <div className="w-12 h-6 bg-surface-200 rounded-full relative">
                                <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full"></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Cognitive Profile Section */}
                <div className="glass-card p-8">
                    <div className="flex items-center gap-4 mb-8">
                        <div className="p-3 bg-indigo-50 rounded-2xl">
                            <Shield className="w-6 h-6 text-indigo-600" />
                        </div>
                        <h3 className="text-xl font-black text-surface-900">Cognitive Profile</h3>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-4">
                            <label className="text-[10px] font-black text-surface-400 uppercase tracking-widest pl-1">Learning Style</label>
                            <div className="flex flex-wrap gap-2">
                                {['Visual', 'Auditory', 'Reading', 'Kinesthetic'].map(style => (
                                    <button 
                                        key={style}
                                        disabled={isUpdating}
                                        onClick={() => updatePreference('learning_style', style.toLowerCase())}
                                        className={`px-4 py-2 rounded-xl text-xs font-bold transition-all border-2 ${
                                            prefs.learning_style === style.toLowerCase() ? 'bg-primary-50 border-primary-600 text-primary-600' : 'bg-surface-50 border-white text-surface-400 hover:border-surface-200'
                                        }`}
                                    >
                                        {style}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="space-y-4">
                            <label className="text-[10px] font-black text-surface-400 uppercase tracking-widest pl-1">Primary Focus Window</label>
                            <select 
                                value={prefs.focus_metabolism || '25'}
                                disabled={isUpdating}
                                onChange={(e) => updatePreference('focus_metabolism', e.target.value)}
                                className="w-full p-4 bg-surface-50 rounded-2xl border-2 border-white font-bold text-surface-900 appearance-none"
                            >
                                <option value="15">15 min (Micro-learning)</option>
                                <option value="25">25 min (Pomodoro)</option>
                                <option value="50">50 min (Deep Work)</option>
                                <option value="90">90 min (Neural Deep Dive)</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* AI Engine Settings */}
                <div className="glass-card p-8 bg-gradient-to-br from-surface-50 to-white">
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-primary-100 rounded-2xl">
                                <Globe className="w-6 h-6 text-primary-600" />
                            </div>
                            <div>
                                <h3 className="text-xl font-black text-surface-900">Neural AI Engine</h3>
                                <p className="text-xs text-surface-400 font-bold tracking-tight mt-0.5">Control the inference logic of your assistant.</p>
                            </div>
                        </div>
                        <div className={`px-3 py-1 text-[10px] font-black rounded-full border ${
                            aiHealth.status === 'connected' 
                            ? 'bg-green-100 text-green-600 border-green-200' 
                            : 'bg-red-100 text-red-600 border-red-200'
                        }`}>
                            {aiHealth.status === 'connected' ? 'CONNECTED' : 'DISCONNECTED'}
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div className="flex items-center justify-between p-4 bg-white/50 rounded-2xl border border-white">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 bg-primary-50 rounded-xl flex items-center justify-center">
                                    <Moon className="w-5 h-5 text-primary-600" />
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-surface-900">Use Custom Fine-tuned Model</p>
                                    <p className="text-xs text-surface-400">Prioritize your proprietary Llama-3.1-8B local model.</p>
                                </div>
                            </div>
                            <div className="w-12 h-6 bg-primary-600 rounded-full relative cursor-pointer shadow-lg shadow-primary-100">
                                <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div>
                            </div>
                        </div>

                        <div className="p-4 bg-surface-900 rounded-2xl text-white">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-[10px] font-black text-primary-400 tracking-widest uppercase">Active Neural Model</span>
                                <span className="text-[10px] font-bold text-surface-400">v0.8.2-alpha</span>
                            </div>
                            <code className="text-sm font-mono opacity-80 text-primary-100">
                                {aiHealth.model || 'neuroplan-llama-3.1-8b-instruct.gguf'}
                            </code>
                        </div>
                    </div>
                </div>

                {/* Danger Zone */}
                <div className="glass-card p-8 border-red-100 bg-red-50/10">
                    <div className="flex items-center gap-4 mb-8">
                        <div className="p-3 bg-red-100 rounded-2xl">
                            <Lock className="w-6 h-6 text-red-600" />
                        </div>
                        <h3 className="text-xl font-black text-surface-900">Security & Account</h3>
                    </div>

                    <div className="flex flex-col md:flex-row gap-4">
                        <Button variant="secondary" className="bg-white border-red-100 text-red-600 hover:bg-red-50">
                            Clear Neural History
                        </Button>
                        <Button onClick={logout} className="bg-red-600 hover:bg-red-700 shadow-red-200">
                           <LogOut className="w-5 h-5 mr-2" /> Sign Out
                        </Button>
                    </div>
                </div>
            </div>

            <div className="text-center">
                <p className="text-[10px] font-black text-surface-300 uppercase tracking-widest">NeuroPlan AI — Production Version 1.0.0</p>
            </div>
        </div>
    )
}

export default SettingsPage
