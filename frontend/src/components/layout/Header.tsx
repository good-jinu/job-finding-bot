"use client";

import React from 'react';
import { Button } from "@/components/ui/button";
import { User, Settings, Briefcase } from "lucide-react";

const Header = () => {
  return (
    <header className="border-b">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <div className="bg-blue-500 w-8 h-8 rounded-lg flex items-center justify-center">
            <Briefcase className="text-white" />
          </div>
          <h1 className="text-xl font-bold">JobFinder AI</h1>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon">
            <Settings className="w-5 h-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <User className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Header;