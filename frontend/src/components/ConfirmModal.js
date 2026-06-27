import { XCircle, AlertTriangle, Info, CheckCircle2, HelpCircle } from 'lucide-react';
import './ConfirmModal.css';

function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  type = 'danger' // 'danger', 'warning', 'info', 'success'
}) {
  if (!isOpen) return null;

  const getIcon = () => {
    switch (type) {
      case 'danger':
        return <XCircle size={40} />;
      case 'warning':
        return <AlertTriangle size={40} />;
      case 'info':
        return <Info size={40} />;
      case 'success':
        return <CheckCircle2 size={40} />;
      default:
        return <HelpCircle size={40} />;
    }
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="confirm-modal-overlay" onClick={handleBackdropClick}>
      <div className="confirm-modal">
        <div className={`confirm-icon confirm-icon-${type}`}>
          {getIcon()}
        </div>
        <h2 className="confirm-title">{title}</h2>
        <p className="confirm-message">{message}</p>
        <div className="confirm-actions">
          {cancelText && (
            <button
              className="btn btn-secondary"
              onClick={onClose}
            >
              {cancelText}
            </button>
          )}
          <button
            className={`btn btn-${type}`}
            onClick={onConfirm}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmModal;
