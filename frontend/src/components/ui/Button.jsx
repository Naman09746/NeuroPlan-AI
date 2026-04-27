import React from 'react'

export const Button = ({ 
  children, 
  variant = 'primary', 
  className = '', 
  isLoading = false,
  ...props 
}) => {
  const variants = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    danger: 'px-6 py-3 bg-red-100 text-red-600 border border-red-200 rounded-2xl font-bold hover:bg-red-200 transition-all',
    ghost: 'px-6 py-3 bg-transparent text-surface-500 rounded-2xl font-medium hover:bg-white hover:text-primary-600 transition-all'
  }

  return (
    <button 
      disabled={isLoading}
      className={`${variants[variant]} flex items-center justify-center gap-2 relative overflow-hidden ${className}`}
      {...props}
    >
      {isLoading ? (
        <>
          <svg className="animate-spin h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Processing...
        </>
      ) : children}
    </button>
  )
}
