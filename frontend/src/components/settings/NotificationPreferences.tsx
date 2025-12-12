import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Separator } from '../ui/separator';

const notificationSettings = [
  {
    category: 'AI Agent Activity',
    settings: [
      { id: 'agent-anomaly', label: 'Security anomaly detected', description: 'Alert when UEBA detects unusual agent behavior', enabled: true },
      { id: 'agent-action', label: 'Autonomous agent actions', description: 'Notify when agents schedule appointments or contact customers', enabled: true },
      { id: 'agent-error', label: 'Agent errors and failures', description: 'Alert when agents encounter errors', enabled: true },
    ],
  },
  {
    category: 'Vehicle Health',
    settings: [
      { id: 'health-critical', label: 'Critical failure predictions', description: 'Immediate alerts for high-probability failures', enabled: true },
      { id: 'health-warning', label: 'Warning-level predictions', description: 'Moderate-risk failure predictions', enabled: true },
      { id: 'health-summary', label: 'Daily fleet health summary', description: 'Daily digest of fleet health status', enabled: false },
    ],
  },
  {
    category: 'Service Scheduling',
    settings: [
      { id: 'schedule-capacity', label: 'Capacity alerts', description: 'Alert when demand exceeds service center capacity', enabled: true },
      { id: 'schedule-conflict', label: 'Scheduling conflicts', description: 'Notify when manual review is needed', enabled: true },
      { id: 'schedule-summary', label: 'Weekly scheduling summary', description: 'Weekly report of scheduling performance', enabled: true },
    ],
  },
  {
    category: 'Manufacturing Quality',
    settings: [
      { id: 'mfg-critical', label: 'Critical CAPA alerts', description: 'Immediate alerts for critical quality issues', enabled: true },
      { id: 'mfg-insights', label: 'New AI insights available', description: 'Notify when AI generates new RCA insights', enabled: true },
      { id: 'mfg-report', label: 'Monthly quality reports', description: 'Monthly manufacturing quality summary', enabled: false },
    ],
  },
];

export function NotificationPreferences() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg mb-1">Notification Preferences</h3>
        <p className="text-sm text-slate-600">Configure how and when you receive notifications</p>
      </div>

      {/* Notification Channels */}
      <div className="bg-slate-50 rounded-lg p-4">
        <h4 className="mb-3">Notification Channels</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <Label>Email Notifications</Label>
              <p className="text-sm text-slate-600">Receive notifications via email</p>
            </div>
            <Switch defaultChecked />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <Label>SMS Notifications</Label>
              <p className="text-sm text-slate-600">Receive critical alerts via SMS</p>
            </div>
            <Switch defaultChecked />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <Label>In-App Notifications</Label>
              <p className="text-sm text-slate-600">Show notifications in the application</p>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
      </div>

      {/* Notification Categories */}
      {notificationSettings.map((category, index) => (
        <div key={index}>
          <h4 className="mb-4">{category.category}</h4>
          <div className="space-y-4">
            {category.settings.map((setting) => (
              <div key={setting.id} className="flex items-center justify-between">
                <div className="flex-1">
                  <Label>{setting.label}</Label>
                  <p className="text-sm text-slate-600">{setting.description}</p>
                </div>
                <Switch defaultChecked={setting.enabled} />
              </div>
            ))}
          </div>
          {index < notificationSettings.length - 1 && <Separator className="mt-6" />}
        </div>
      ))}

      {/* Action Buttons */}
      <div className="flex justify-end space-x-3 pt-6 border-t">
        <Button variant="outline">Reset to Default</Button>
        <Button>Save Preferences</Button>
      </div>
    </div>
  );
}
