import { X, Phone, CheckCircle, Clock } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';

interface CustomerInteractionModalProps {
  onClose: () => void;
}

const transcript = [
  {
    id: 1,
    speaker: 'AI Agent',
    text: 'Hello, Mr. Kumar. This is your vehicle service assistant. My diagnostics show that your vehicle (VIN: MH04XY1234) may have a transmission issue that needs attention.',
    time: '10:46:15',
  },
  {
    id: 2,
    speaker: 'Customer',
    text: 'Oh really? I haven\'t noticed anything unusual. What kind of issue?',
    time: '10:46:28',
    isVoice: true,
  },
  {
    id: 3,
    speaker: 'AI Agent',
    text: 'Our sensors detected potential clutch plate wear based on vibration patterns and transmission temperature data. This is predicted with 92% confidence. It\'s best to address this before it becomes a more serious problem.',
    time: '10:46:35',
  },
  {
    id: 4,
    speaker: 'Customer',
    text: 'That sounds important. What do I need to do?',
    time: '10:46:52',
    isVoice: true,
  },
  {
    id: 5,
    speaker: 'AI Agent',
    text: 'I can schedule a service appointment for you at our Mumbai Central Service Center. I have availability tomorrow at 10:00 AM or 2:00 PM. Which time works better for you?',
    time: '10:46:58',
  },
  {
    id: 6,
    speaker: 'Customer',
    text: '10 AM tomorrow works for me.',
    time: '10:47:15',
    isVoice: true,
  },
  {
    id: 7,
    speaker: 'AI Agent',
    text: 'Perfect! I\'ve booked your appointment for December 14th at 10:00 AM at Mumbai Central Service Center. The estimated service time is 4-6 hours. You\'ll receive a confirmation SMS shortly with all the details. Is there anything else I can help you with?',
    time: '10:47:22',
  },
  {
    id: 8,
    speaker: 'Customer',
    text: 'No, that\'s all. Thank you!',
    time: '10:47:45',
    isVoice: true,
  },
  {
    id: 9,
    speaker: 'AI Agent',
    text: 'You\'re welcome, Mr. Kumar. We look forward to seeing you tomorrow. Have a great day!',
    time: '10:47:50',
  },
];

export function CustomerInteractionModal({ onClose }: CustomerInteractionModalProps) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <CardHeader className="flex-shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Customer Engagement Agent - Voice Interaction</CardTitle>
              <p className="text-sm text-slate-600 mt-1">
                Autonomous AI agent conversation with vehicle owner
              </p>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto">
          {/* Interaction Metadata */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-slate-600">Customer</p>
                <p className="text-sm">Rajesh Kumar</p>
              </div>
              <div>
                <p className="text-xs text-slate-600">VIN</p>
                <p className="text-sm font-mono">MH04XY1234</p>
              </div>
              <div>
                <p className="text-xs text-slate-600">Channel</p>
                <div className="flex items-center space-x-1">
                  <Phone className="w-3 h-3" />
                  <p className="text-sm">Voice Call</p>
                </div>
              </div>
              <div>
                <p className="text-xs text-slate-600">Duration</p>
                <p className="text-sm">1m 35s</p>
              </div>
            </div>
          </div>

          {/* Interaction Status */}
          <div className="flex items-center justify-between mb-4">
            <Badge variant="secondary" className="bg-green-100 text-green-700">
              <CheckCircle className="w-3 h-3 mr-1" />
              Call Completed Successfully
            </Badge>
            <Badge variant="secondary" className="bg-purple-100 text-purple-700">
              Appointment Auto-Scheduled
            </Badge>
          </div>

          <Separator className="my-4" />

          {/* Transcript */}
          <div className="space-y-4">
            <h3 className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-slate-600" />
              <span>Conversation Transcript</span>
            </h3>

            {transcript.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.speaker === 'AI Agent' ? 'justify-start' : 'justify-end'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.speaker === 'AI Agent'
                      ? 'bg-blue-50 border border-blue-200'
                      : 'bg-green-50 border border-green-200'
                  }`}
                >
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xs">
                      {message.speaker === 'AI Agent' ? '🤖' : '👤'}
                    </span>
                    <span className="text-xs">{message.speaker}</span>
                    <span className="text-xs text-slate-500">{message.time}</span>
                    {message.isVoice && (
                      <Badge variant="secondary" className="text-xs px-1 py-0 bg-purple-100 text-purple-700">
                        Voice
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm">{message.text}</p>
                </div>
              </div>
            ))}
          </div>

          <Separator className="my-4" />

          {/* Outcome Summary */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="mb-2">Interaction Outcome</h3>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span>
                  <strong>Service Appointment Scheduled:</strong> December 14, 2025 at 10:00 AM
                </span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span>
                  <strong>Confirmation SMS Sent:</strong> +91-98765-43210
                </span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span>
                  <strong>Service Bay Reserved:</strong> Bay 1, Mumbai Central
                </span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span>
                  <strong>Customer Sentiment:</strong> Positive (NLP Analysis: 8.5/10)
                </span>
              </li>
            </ul>
          </div>
        </CardContent>

        <div className="flex-shrink-0 p-4 border-t flex justify-end space-x-2">
          <Button variant="outline">Download Transcript</Button>
          <Button variant="outline">View Customer Profile</Button>
          <Button onClick={onClose}>Close</Button>
        </div>
      </Card>
    </div>
  );
}
