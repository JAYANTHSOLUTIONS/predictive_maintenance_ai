import { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Progress } from '../ui/progress';
import { ArrowLeft, ArrowRight, Check } from 'lucide-react';

interface RegisterProps {
  onRegister: () => void;
  onSwitchToLogin: () => void;
}

export function Register({ onRegister, onSwitchToLogin }: RegisterProps) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: '',
    location: '',
    plant: '',
  });

  const handleNext = () => {
    if (step < 3) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onRegister();
  };

  const progress = (step / 3) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-8">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow-xl p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl mb-2">Create Your Account</h1>
          <p className="text-slate-600">Join the OEM Aftersales Intelligence Platform</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            <span className="text-sm">Step {step} of 3</span>
            <span className="text-sm text-slate-600">{progress.toFixed(0)}% Complete</span>
          </div>
          <Progress value={progress} />
          <div className="flex justify-between mt-3 text-xs text-slate-600">
            <span className={step === 1 ? 'text-blue-600' : ''}>Account Details</span>
            <span className={step === 2 ? 'text-blue-600' : ''}>Role Selection</span>
            <span className={step === 3 ? 'text-blue-600' : ''}>Location Assignment</span>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Step 1: Account Details */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <Label htmlFor="fullName">Full Name</Label>
                <Input
                  id="fullName"
                  placeholder="John Doe"
                  value={formData.fullName}
                  onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                  className="mt-1"
                  required
                />
              </div>
              <div>
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="john.doe@company.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="mt-1"
                  required
                />
              </div>
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Create a strong password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="mt-1"
                  required
                />
              </div>
              <div>
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Re-enter your password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="mt-1"
                  required
                />
              </div>
            </div>
          )}

          {/* Step 2: Role Selection */}
          {step === 2 && (
            <div className="space-y-6">
              <div>
                <Label>Select Your Role</Label>
                <RadioGroup
                  value={formData.role}
                  onValueChange={(value) => setFormData({ ...formData, role: value })}
                  className="mt-3 space-y-3"
                >
                  <div className="flex items-start space-x-3 border rounded-lg p-4 hover:bg-slate-50 cursor-pointer">
                    <RadioGroupItem value="service-manager" id="service-manager" className="mt-1" />
                    <div>
                      <Label htmlFor="service-manager" className="cursor-pointer">
                        Service Center Manager
                      </Label>
                      <p className="text-sm text-slate-600">
                        Manage service operations, scheduling, and customer interactions
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3 border rounded-lg p-4 hover:bg-slate-50 cursor-pointer">
                    <RadioGroupItem value="manufacturing-engineer" id="manufacturing-engineer" className="mt-1" />
                    <div>
                      <Label htmlFor="manufacturing-engineer" className="cursor-pointer">
                        Manufacturing Engineer
                      </Label>
                      <p className="text-sm text-slate-600">
                        Access quality insights, RCA/CAPA data, and production analytics
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3 border rounded-lg p-4 hover:bg-slate-50 cursor-pointer">
                    <RadioGroupItem value="system-admin" id="system-admin" className="mt-1" />
                    <div>
                      <Label htmlFor="system-admin" className="cursor-pointer">
                        System Administrator
                      </Label>
                      <p className="text-sm text-slate-600">
                        Full access to security monitoring, UEBA, and system configurations
                      </p>
                    </div>
                  </div>
                </RadioGroup>
              </div>
            </div>
          )}

          {/* Step 3: Location Assignment */}
          {step === 3 && (
            <div className="space-y-6">
              <div>
                <Label htmlFor="location">Primary Location</Label>
                <Select
                  value={formData.location}
                  onValueChange={(value) => setFormData({ ...formData, location: value })}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select your location" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="mumbai">Mumbai, Maharashtra</SelectItem>
                    <SelectItem value="chennai">Chennai, Tamil Nadu</SelectItem>
                    <SelectItem value="bangalore">Bangalore, Karnataka</SelectItem>
                    <SelectItem value="delhi">Delhi NCR</SelectItem>
                    <SelectItem value="pune">Pune, Maharashtra</SelectItem>
                    <SelectItem value="hyderabad">Hyderabad, Telangana</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="plant">Manufacturing Plant / Service Center</Label>
                <Select
                  value={formData.plant}
                  onValueChange={(value) => setFormData({ ...formData, plant: value })}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select your facility" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="plant-001">Plant 001 - Manesar</SelectItem>
                    <SelectItem value="plant-002">Plant 002 - Sanand</SelectItem>
                    <SelectItem value="sc-mumbai-central">Service Center - Mumbai Central</SelectItem>
                    <SelectItem value="sc-chennai-north">Service Center - Chennai North</SelectItem>
                    <SelectItem value="sc-bangalore-east">Service Center - Bangalore East</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
                <div className="flex items-start space-x-3">
                  <Check className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="text-sm">
                      By creating an account, you agree to the Terms of Service and Privacy Policy of the OEM Aftersales Intelligence Platform.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8">
            <div>
              {step > 1 ? (
                <Button type="button" variant="outline" onClick={handleBack}>
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back
                </Button>
              ) : (
                <Button type="button" variant="ghost" onClick={onSwitchToLogin}>
                  Already have an account?
                </Button>
              )}
            </div>
            <div>
              {step < 3 ? (
                <Button type="button" onClick={handleNext}>
                  Next
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button type="submit">
                  Create Account
                  <Check className="w-4 h-4 ml-2" />
                </Button>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
