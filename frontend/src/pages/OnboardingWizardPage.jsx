import React, { useState } from 'react'
import { Brain, Zap, Target, BookOpen, ChevronRight, Check } from 'lucide-react'
import { Button } from '@/components/ui/Button'

const steps = [
    {
        id: 'style',
        title: 'Your Learning Style',
        subtitle: 'How does your brain absorb information best?',
        options: [
            { id: 'visual', label: 'Visual', desc: 'Diagrams, spatial layouts, and mental maps.', icon: Zap },
            { id: 'auditory', label: 'Auditory', desc: 'Listening, discussions, and verbal repetition.', icon: Brain },
            { id: 'reading', label: 'Reading', desc: 'Text-heavy resources and extensive note-taking.', icon: BookOpen },
            { id: 'kinesthetic', label: 'Kinesthetic', desc: 'Hands-on practice and interactive exercises.', icon: Target }
        ]
    },
    {
        id: 'focus',
        title: 'Focus Metabolism',
        subtitle: 'What is your natural deep-work capacity?',
        options: [
            { id: '15', label: 'Micro-learning', desc: '15-minute high-intensity bursts.', icon: Zap },
            { id: '25', label: 'Pomodoro', desc: 'Standard 25-minute focus intervals.', icon: Brain },
            { id: '50', label: 'Deep Work', desc: '50-minute focused sessions.', icon: Target },
            { id: '90', label: 'Flow State', desc: 'Extended 90-minute neural dives.', icon: BookOpen }
        ]
    }
]

const OnboardingWizardPage = () => {
    const [currentStep, setCurrentStep] = useState(0)
    const [selections, setSelections] = useState({})

    const handleSelect = (optionId) => {
        setSelections({ ...selections, [steps[currentStep].id]: optionId })
    }

    const nextStep = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(currentStep + 1)
        } else {
            console.log('Onboarding Complete:', selections)
            // Redirect to dashboard
        }
    }

    const step = steps[currentStep]

    return (
        <div className="min-h-screen bg-surface-50 flex items-center justify-center p-6">
            <div className="max-w-4xl w-full">
                <div className="text-center mb-16">
                    <div className="w-16 h-16 bg-primary-600 rounded-3xl rotate-45 flex items-center justify-center mx-auto mb-8 shadow-2xl shadow-primary-200">
                        <Brain className="w-8 h-8 text-white -rotate-45" />
                    </div>
                    <h1 className="text-5xl font-black text-surface-900 tracking-tight">Configure Your Neural Profile</h1>
                    <p className="text-surface-400 mt-4 font-bold text-lg">Step {currentStep + 1} of {steps.length}: {step.title}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {step.options.map((option) => (
                        <button
                            key={option.id}
                            onClick={() => handleSelect(option.id)}
                            className={`p-8 rounded-3xl text-left transition-all border-4 relative overflow-hidden group ${
                                selections[step.id] === option.id 
                                ? 'bg-white border-primary-600 shadow-xl shadow-primary-100 scale-[1.02]' 
                                : 'bg-white/50 border-white hover:border-surface-200'
                            }`}
                        >
                            {selections[step.id] === option.id && (
                                <div className="absolute top-4 right-4 w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center text-white">
                                    <Check className="w-4 h-4" />
                                </div>
                            )}
                            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-6 transition-colors ${
                                selections[step.id] === option.id ? 'bg-primary-50' : 'bg-surface-50'
                            }`}>
                                <option.icon className={`w-6 h-6 ${
                                    selections[step.id] === option.id ? 'text-primary-600' : 'text-surface-400'
                                }`} />
                            </div>
                            <h3 className="text-xl font-black text-surface-900 mb-2">{option.label}</h3>
                            <p className="text-sm text-surface-400 font-medium leading-relaxed">{option.desc}</p>
                        </button>
                    ))}
                </div>

                <div className="mt-16 flex items-center justify-between bg-white p-6 rounded-3xl shadow-sm border border-white">
                    <div className="flex gap-2">
                        {steps.map((_, i) => (
                            <div key={i} className={`h-2 rounded-full transition-all ${
                                i === currentStep ? 'w-12 bg-primary-600' : 'w-4 bg-surface-100'
                            }`} />
                        ))}
                    </div>
                    <Button 
                        disabled={!selections[step.id]}
                        onClick={nextStep}
                        className="h-14 px-8 bg-surface-900 hover:bg-black group"
                    >
                        {currentStep === steps.length - 1 ? 'Activate Engine' : 'Next Integration'}
                        <ChevronRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                    </Button>
                </div>
            </div>
        </div>
    )
}

export default OnboardingWizardPage
