import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Brain, ArrowRight, Github } from 'lucide-react'
import { Input } from '../components/ui/Input'
import { Button } from '../components/ui/Button'
import { useAuthStore } from '../store/useAuthStore'
import toast from 'react-hot-toast'

const LoginPage = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { login, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await login(email, password)
      toast.success('Welcome back!')
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-surface-50 relative overflow-hidden">
      {/* Decorative blobs */}
      <div className="absolute top-0 -left-20 w-96 h-96 bg-primary-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
      <div className="absolute bottom-0 -right-20 w-96 h-96 bg-indigo-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse delay-75"></div>

      <div className="w-full max-w-lg glass-card p-10 relative z-10 animate-slide-up">
        <div className="flex flex-col items-center mb-10 text-center">
          <div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-200 mb-6 group cursor-pointer hover:rotate-6 transition-transform">
            <Brain className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-black text-surface-900 mb-2">NeuroPlan AI</h1>
          <p className="text-surface-500 font-medium">Precision learning for high-performance minds.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
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
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          
          <div className="flex justify-end">
            <Link to="#" className="text-sm font-bold text-primary-600 hover:text-primary-700 transition-colors">
              Forgot password?
            </Link>
          </div>

          <Button type="submit" className="w-full" isLoading={isLoading}>
            Sign In <ArrowRight className="w-5 h-5" />
          </Button>

          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-surface-200"></div>
            </div>
            <div className="relative flex justify-center text-xs font-bold uppercase">
              <span className="bg-white px-4 text-surface-400">Or continue with</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Button variant="secondary" className="w-full" type="button">
              <Github className="w-5 h-5" /> GitHub
            </Button>
            <Button variant="secondary" className="w-full" type="button">
              <img src="https://www.google.com/favicon.ico" alt="Google" className="w-4 h-4" /> Google
            </Button>
          </div>
        </form>

        <p className="mt-10 text-center text-sm font-medium text-surface-500">
          Don't have an account?{' '}
          <Link to="/register" className="font-bold text-primary-600 hover:text-primary-700 underline-offset-4 hover:underline">
            Join the collective
          </Link>
        </p>
      </div>
    </div>
  )
}

export default LoginPage
