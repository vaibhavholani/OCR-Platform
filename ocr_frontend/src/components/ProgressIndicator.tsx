import React from "react";
import { Check } from "lucide-react";

interface ProgressStep {
  id: number;
  name: string;
  description: string;
}

interface ProgressIndicatorProps {
  currentStep: number;
  steps?: ProgressStep[];
}

const ProgressIndicator = ({ currentStep, steps }: ProgressIndicatorProps) => {
  const defaultSteps = [
    { id: 1, name: "Upload", description: "Upload your document" },
    { id: 2, name: "Select Template", description: "Select a template" },
    { id: 3, name: "Edit Data and Save", description: "Edit data and save" },
    { id: 4, name: "Export", description: "Export your data" },
  ];

  const stepsToUse = steps || defaultSteps;

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        {stepsToUse.map((step, index) => (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`
                w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium
                ${
                  currentStep > step.id
                    ? "bg-green-500 text-white"
                    : currentStep === step.id
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-gray-500"
                }
              `}
              >
                {currentStep > step.id ? (
                  <Check className="h-5 w-5" />
                ) : (
                  step.id
                )}
              </div>
              <div className="mt-2 text-center">
                <p
                  className={`text-xs font-medium ${
                    currentStep >= step.id ? "text-gray-900" : "text-gray-500"
                  }`}
                >
                  {step.name}
                </p>
                <p
                  className={`text-xs ${
                    currentStep >= step.id ? "text-gray-600" : "text-gray-400"
                  }`}
                >
                  {step.description}
                </p>
              </div>
            </div>
            {index < stepsToUse.length - 1 && (
              <div
                className={`
                flex-1 h-0.5 mx-4 mt-[-20px]
                ${currentStep > step.id ? "bg-green-500" : "bg-gray-200"}
              `}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProgressIndicator;
