"use client";

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, Plus, RefreshCw, AlertCircle, CheckCircle2 } from "lucide-react";

interface Provider {
  name: str;
  display_name: str;
  description: str;
  supported_auth_types: str[];
  supported_capabilities: str[];
}

export default function IntegrationsPage() {
  const [providers, setProviders] = useState<Record<string, Provider>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In production this would fetch from /api/integrations/providers
    // Here we mock the response for the dashboard
    setTimeout(() => {
      setProviders({
        "hubspot": {
          name: "hubspot",
          display_name: "HubSpot",
          description: "Sync Companies, Contacts, and Deals natively.",
          supported_auth_types: ["oauth2"],
          supported_capabilities: ["companies", "contacts", "opportunities", "webhooks", "incremental_sync"]
        },
        "salesforce": {
          name: "salesforce",
          display_name: "Salesforce",
          description: "Sync Accounts, Contacts, Opportunities, and Events.",
          supported_auth_types: ["oauth2"],
          supported_capabilities: ["companies", "contacts", "opportunities", "webhooks", "incremental_sync"]
        }
      });
      setLoading(false);
    }, 1000);
  }, []);

  const handleConnect = (providerName: string) => {
    // Redirect to backend OAuth generation endpoint
    window.location.href = `/api/integrations/auth/${providerName}/url?redirect_uri=${window.location.origin}/dashboard/settings/integrations/callback`;
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Integration Hub</h1>
        <p className="text-muted-foreground mt-2">
          Connect AVENOR-AI to your CRM and communication tools.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
        {loading ? (
          <div className="flex justify-center items-center col-span-3 py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : (
          Object.values(providers).map((provider) => (
            <Card key={provider.name} className="glass-card hover:glass-card-hover transition-all duration-300">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="text-xl">{provider.display_name}</CardTitle>
                  <Badge variant="outline" className="bg-primary/10 text-primary">Official</Badge>
                </div>
                <CardDescription className="mt-2 text-sm leading-relaxed">
                  {provider.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2 mb-6">
                  {provider.supported_capabilities.map((cap) => (
                    <Badge key={cap} variant="secondary" className="text-xs">
                      {cap.replace('_', ' ')}
                    </Badge>
                  ))}
                </div>
                <Button 
                  onClick={() => handleConnect(provider.name)}
                  className="w-full font-medium"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Connect {provider.display_name}
                </Button>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
