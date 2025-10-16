import './WizardSteps.css';

function WizardSteps({ currentStep, steps }) {
  return (
    <div className="wizard-steps">
      {steps.map((step, index) => (
        <div key={index} className="wizard-step-wrapper">
          <div
            className={`wizard-step ${
              index + 1 === currentStep
                ? 'active'
                : index + 1 < currentStep
                ? 'completed'
                : ''
            }`}
          >
            <div className="step-number">
              {index + 1 < currentStep ? (
                <span className="step-check">✓</span>
              ) : (
                <span>{index + 1}</span>
              )}
            </div>
            <div className="step-info">
              <div className="step-label">{step.label}</div>
              <div className="step-description">{step.description}</div>
            </div>
          </div>
          {index < steps.length - 1 && (
            <div
              className={`wizard-line ${
                index + 1 < currentStep ? 'completed' : ''
              }`}
            />
          )}
        </div>
      ))}
    </div>
  );
}

export default WizardSteps;
