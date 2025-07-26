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

  useEffect(() => {
    const storedInfo = localStorage.getItem('studyInfo');
    if (storedInfo) {
      setStudyInfo(JSON.parse(storedInfo));
      setIsFirstVisit(false);
    } else {
      setIsFirstVisit(true);
    }
  }, []);

  const saveStudyInfo = (info: StudyInfo) => {
    localStorage.setItem('studyInfo', JSON.stringify(info));
    setStudyInfo(info);
    setIsFirstVisit(false);
  };

  const clearStudyInfo = () => {
    localStorage.removeItem('studyInfo');
    setStudyInfo(null);
    setIsFirstVisit(true);
  };

  return {
    isFirstVisit,
    studyInfo,
    saveStudyInfo,
    clearStudyInfo
  };
}
