export type AudioPlayerProps = {
  isActive: boolean;
  audioSrc: string;
  waveHeight: number;
  isResetWaveForm: boolean;
};
export type Transcription = {
  text: string;
  start: number;
  end: number;
  speaker: string;
};
export type Transcriptions = Transcription[];

export type AudioRecord = {
  file_name: string;
  url: string;
  uploaded_date: Date;
  formatted_date: string;
  duration: string | null;
};

export type statusCode = {
  status: number;
};

export type SoapNote = {
  Subjective: {
    Chief_Complaint: string;
    History_of_Present_Illness: string;
    Past_Medical_History: {
      Past_medical_history: string;
      Allergies: boolean;
    };
    Family_History: {
      Condition: string;
    };
    Social_History: {
      Marital_status: string;
      Place_of_residence: string;
      Alcohol: string;
      Drugs: string;
      Smoking_habit: {
        Per_day: number;
      };
      Exercise: {
        Frequency: string;
      };
      Review_of_Systems: string[];
    };
  };
  Objective: {
    Physical_Examination: string;
    Laboratory_Results: {
      Result: string;
    }[];
    Imaging_Results: {
      Result: string;
    }[];
  };
  Assessment: {
    Diagnoses: string[];
    Differential_Diagnoses: string[];
  };
  Plan: {
    Treatment: string[];
    Follow_Up: string;
    Patient_Education: {
      Recommendations: string[];
    };
    Referrals: string[];
  };
};

export type SoapJsonType = {
  SOAP_Note: {
    [key: string]: any;
  };
};
export type GenericJson = {
  [key: string]: any;
};
export type Content = {
  title: string;
  content: string;
};

export type EvaluatedFile = {
  file_name: string;
  wer_score: string;
};

export type ColorMap = {
  [key: string]: string;
};

export type Entity = {
  entity_group: string;
  start: number;
  end: number;
  word: string;
};

export type SubSection = {
  text: string;
  entities: Entity[];
};

export type Section = SubSection | { [sub_title: string]: SubSection };

export type ExtractedEntities = {
  [parentKey: string]: {
    [sectionName: string]: Section;
  };
};
