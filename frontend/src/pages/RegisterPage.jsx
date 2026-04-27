import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Brain, ArrowRight } from 'lucide-react'
import { Input } from '../components/ui/Input'
import { Button } from '../components/ui/Button'
import { useAuthStore } from '../store/useAuthStore'
import toast from 'react-hot-toast'

const RegisterPage = () => {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { register, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await register(name, email, password)
      toast.success('Account created successfully!')
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-surface-50 relative overflow-hidden">
      <div className="absolute top-0 -right-20 w-96 h-96 bg-primary-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
      <div className="absolute bottom-0 -left-20 w-96 h-96 bg-indigo-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse delay-75"></div>

      <div className="w-full max-w-lg glass-card p-10 relative z-10 animate-slide-up">
        <div className="flex flex-col items-center mb-10 text-center">
          <div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-200 mb-6 transition-transform hover:scale-110">
            <Brain className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-black text-surface-900 mb-2">Join NeuroPlan</h1>
          <p className="text-surface-500 font-medium">Start your journey to cognitive optimization.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Input 
            label="Full Name"
            placeholder="Naman Joshi"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <Input 
            label="Email Address"
            type="email"
            placeholder="naman@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input 
            label="Password"
            type="password"
            placeholder="Minimum 8 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
          
          <div className="flex items-center gap-2 ml-1">
            <input type="checkbox" required className="w-4 h-4 rounded text-primary-600 focus:ring-primary-500 border-surface-200" />
            <span className="text-xs font-bold text-surface-500 uppercase tracking-wider">
              I agree to the <Link to="#" className="text-primary-600">Privacy Policy</Link>
            </span>
          </div>

          <Button type="submit" className="w-full" isLoading={isLoading}>
            Initialize Account <ArrowRight className="w-5 h-5" />
          </Button>
        </form>

        <p className="mt-10 text-center text-sm font-medium text-surface-500">
          Already a member?{' '}
          <Link to="/login" className="font-bold text-primary-600 hover:text-primary-700 underline-offset-4 hover:underline">
            Access your node
          </Link>
        </p>
      </div>
    </div>
  )
}

export default RegisterPage
