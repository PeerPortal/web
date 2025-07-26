'use client';

import React from 'react';

interface AuthHeaderProps {
  title: string;
  question: string;
  actionText: string;
  actionPath: string;
}

function AuthHeader({
  title,
  question,
  actionText,
  actionPath
}: AuthHeaderProps) {
  return (
    <div className="gap-1">
      <h3 className="text-2xl font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-lg">
        {question}{' '}
        <a href={actionPath} className="underline">
          {actionText}
        </a>
      </p>
    </div>
  );
}

export default AuthHeader;
