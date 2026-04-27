import React from 'react'
import { AlertCircle, RotateCcw, Home } from 'lucide-react'
import { Button } from './Button'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Neural Logic Failure:', error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-surface-50 flex flex-col items-center justify-center p-10 text-center">
          <div className="w-24 h-24 bg-red-50 rounded-[32px] flex items-center justify-center mb-8 border-2 border-red-100 shadow-xl shadow-red-200/20">
            <AlertCircle className="w-12 h-12 text-red-600 animate-pulse" />
          </div>
          
          <h1 className="text-4xl font-black text-surface-900 tracking-tighter mb-4">Neural Logic Failure</h1>
          <p className="text-surface-500 font-medium max-w-md mb-10 leading-relaxed">
            A critical intercept in the cognitive flow has occurred. The system has safely isolated the corrupted module to prevent recursive failures.
          </p>

          <div className="flex flex-col sm:flex-row gap-4">
            <Button onClick={this.handleReset} className="px-8 py-4">
              <RotateCcw className="w-5 h-5 mr-2" /> Re-initialize App
            </Button>
            <Button variant="secondary" onClick={() => window.location.href = '/'} className="px-8 py-4 bg-white">
              <Home className="w-5 h-5 mr-2" /> Return to Home
            </Button>
          </div>

          <div className="mt-16 p-4 bg-white/50 rounded-2xl border border-white max-w-2xl overflow-hidden">
            <div className="text-[10px] font-black text-surface-400 uppercase tracking-widest mb-2">Internal Error Log</div>
            <pre className="text-left text-[10px] font-mono text-surface-400 overflow-x-auto whitespace-pre-wrap">
              {this.state.error?.toString()}
            </pre>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
