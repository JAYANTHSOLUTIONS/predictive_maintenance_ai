import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { UserProfile } from './UserProfile';
import { NotificationPreferences } from './NotificationPreferences';
import { ServiceCenterConfig } from './ServiceCenterConfig';
import { ApiKeyManagement } from './ApiKeyManagement';

export function Settings() {
  const [activeTab, setActiveTab] = useState('profile');

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl mb-2">Settings & Customizations</h1>
        <p className="text-slate-600">Manage your account, preferences, and system configurations</p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="profile">User Profile</TabsTrigger>
              <TabsTrigger value="notifications">Notifications</TabsTrigger>
              <TabsTrigger value="service-center">Service Center</TabsTrigger>
              <TabsTrigger value="api-keys">API Keys</TabsTrigger>
            </TabsList>

            <TabsContent value="profile" className="mt-6">
              <UserProfile />
            </TabsContent>

            <TabsContent value="notifications" className="mt-6">
              <NotificationPreferences />
            </TabsContent>

            <TabsContent value="service-center" className="mt-6">
              <ServiceCenterConfig />
            </TabsContent>

            <TabsContent value="api-keys" className="mt-6">
              <ApiKeyManagement />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
