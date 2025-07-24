'use client';

import { useRouter } from 'next/navigation';
import { useQueryState } from 'nuqs';
import React, { useEffect, useState } from 'react';
import AuthHeader from '@/components/auth/auth-header';
// import LoginForm from '@/components/auth/login-form';
// import OrDivider from '@/components/auth/or-divider';
// import SocialLoginButton from '@/components/auth/social-login-button';
// import useSupabaseAuth from '@/lib/hooks/use-supabase-auth';
import { View } from 'lucide-react';

export default function Page() {
  const router = useRouter();
  //   const { session } = useSupabaseAuth();
  // const [redirect] = useQueryState('redirect');
  //   const [isRedirecting, setIsRedirecting] = useState(false);

  //   useEffect(() => {
  //     if (session && !isRedirecting) {
  //       setIsRedirecting(true);
  //       router.push(redirect || '/');
  //     }
  //   }, [session, redirect, router, isRedirecting]);

  return (
    <div className="flex justify-center items-center">
      <div className="max-w-4xl w-full gap-4">
        {/* <AuthHeader
          title="登录"
          question="没有账号？"
          actionText="注册"
          actionPath={`/signup${redirect ? `?redirect=${redirect}` : ''}`}
        /> */}
        {/* <LoginForm
          redirect={redirect || undefined}
          onLoginSuccess={() => setIsRedirecting(true)}
        />
        <OrDivider />
        <SocialLoginButton /> */}
      </div>
    </div>
  );
}
