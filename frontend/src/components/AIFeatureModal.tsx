import { useState } from 'react';
import { X, Copy, Download, Loader2, Check } from 'lucide-react';

interface AIFeatureModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  content: string | React.ReactNode;
  isLoading?: boolean;
}

export function AIFeatureModal({ isOpen, onClose, title, content, isLoading }: AIFeatureModalProps) {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopy = () => {
    if (typeof content === 'string') {
      navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (typeof content === 'string') {
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${title.toLowerCase().replace(/\s+/g, '-')}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
              <span className="ml-3 text-gray-600">Generating with AI...</span>
            </div>
          ) : (
            <div className="prose max-w-none">
              {typeof content === 'string' ? (
                <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                  {content}
                </div>
              ) : (
                content
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        {!isLoading && typeof content === 'string' && (
          <div className="flex items-center justify-end gap-3 p-6 border-t bg-gray-50">
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-primary-600" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>Copy</span>
                </>
              )}
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default AIFeatureModal;
