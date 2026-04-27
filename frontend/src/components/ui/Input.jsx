import React from 'react'

export const Input = ({ label, error, className = '', ...props }) => {
  return (
    <div className={`space-y-1.5 ${className}`}>
      {label && (
        <label className="text-sm font-bold text-surface-700 ml-1">
          {label}
        </label>
      )}
      <input
        className={`w-full px-5 py-4 bg-white/50 backdrop-blur-sm border-2 rounded-2xl outline-none transition-all duration-300 font-medium
          ${error 
            ? 'border-red-200 focus:border-red-500 focus:ring-4 focus:ring-red-500/10' 
            : 'border-surface-100 focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10'
          }`}
        {...props}
      />
      {error && (
        <p className="text-xs font-bold text-red-500 ml-1 mt-1">
          {error}
        </p>
      )}
    </div>
  )
}
