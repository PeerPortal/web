'use client';

import { useState, useEffect } from 'react';

export type UserType = 'studying' | 'planning';

export interface StudyInfo {
  userType: UserType;
  region: string;
  school: string;
  major: string;
}

export function useFirstVisit() {
  const [isFirstVisit, setIsFirstVisit] = useState<boolean | null>(null);
  const [studyInfo, setStudyInfo] = useState<StudyInfo | null>(null);
  const [showAfterRegistration, setShowAfterRegistration] =
    useState<boolean>(false);

  useEffect(() => {
    const storedInfo = localStorage.getItem('studyInfo');
    const shouldShowAfterReg =
      localStorage.getItem('showFirstVisitAfterRegistration') === 'true';

    if (storedInfo) {
      setStudyInfo(JSON.parse(storedInfo));
      setIsFirstVisit(false);
    } else {
      setIsFirstVisit(true);
    }

    setShowAfterRegistration(shouldShowAfterReg);
  }, []);

  const saveStudyInfo = (info: StudyInfo) => {
    localStorage.setItem('studyInfo', JSON.stringify(info));
    localStorage.removeItem('showFirstVisitAfterRegistration');
    setStudyInfo(info);
    setIsFirstVisit(false);
    setShowAfterRegistration(false);
  };

  const clearStudyInfo = () => {
    localStorage.removeItem('studyInfo');
    localStorage.removeItem('showFirstVisitAfterRegistration');
    setStudyInfo(null);
    setIsFirstVisit(true);
    setShowAfterRegistration(false);
  };

  const triggerAfterRegistration = () => {
    localStorage.setItem('showFirstVisitAfterRegistration', 'true');
    setShowAfterRegistration(true);
  };

  return {
    isFirstVisit,
    studyInfo,
    saveStudyInfo,
    clearStudyInfo,
    showAfterRegistration,
    triggerAfterRegistration
  };
}
