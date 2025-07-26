'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { UserTypeSelection } from './user-type-selection';
import { StudyInfoForm } from './study-info-form';
import { useFirstVisit } from '@/hooks/use-first-visit';
import type { UserType, StudyInfo } from '@/hooks/use-first-visit';

export function FirstVisitModal() {
  const { isFirstVisit, saveStudyInfo } = useFirstVisit();
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState<'userType' | 'studyInfo'>('userType');
  const [selectedUserType, setSelectedUserType] = useState<UserType | null>(
    null
  );

  useEffect(() => {
    if (isFirstVisit === true) {
      setIsOpen(true);
    }
  }, [isFirstVisit]);

  const handleUserTypeSelect = (type: UserType) => {
    setSelectedUserType(type);
    setStep('studyInfo');
  };

  const handleStudyInfoSubmit = (info: StudyInfo) => {
    saveStudyInfo(info);
    setIsOpen(false);
  };

  const handleBack = () => {
    setStep('userType');
    setSelectedUserType(null);
  };

  if (isFirstVisit === null) {
    return null;
  }

  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogContent className="max-w-fit border-0 p-0 overflow-hidden">
        {step === 'userType' && (
          <UserTypeSelection onSelect={handleUserTypeSelect} />
        )}
        {step === 'studyInfo' && selectedUserType && (
          <StudyInfoForm
            userType={selectedUserType}
            onSubmit={handleStudyInfoSubmit}
            onBack={handleBack}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}
