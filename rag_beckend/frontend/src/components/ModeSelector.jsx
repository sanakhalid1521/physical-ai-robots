import React from 'react';
import './ModeSelector.css';

const ModeSelector = ({ currentMode, onModeChange, onTextSelection }) => {
  return (
    <div className="mode-selector">
      <button
        className={currentMode === 'book' ? 'active' : ''}
        onClick={() => onModeChange('book')}
      >
        Full Book
      </button>
      <button
        className={currentMode === 'selection' ? 'active' : ''}
        onClick={onTextSelection}
      >
        Selected Text
      </button>
    </div>
  );
};

export default ModeSelector;