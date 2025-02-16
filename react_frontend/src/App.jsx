import React, { useState, useRef } from 'react';
import { Camera, Image, Share2, Download, Sparkles, RefreshCw } from 'lucide-react';
import { Transition } from '@headlessui/react';

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
    } catch (err) {
      console.error("Error accessing camera:", err);
    }
  };

  React.useEffect(() => {
    startCamera();
  }, []);

  const capturePhoto = async () => {
    setIsProcessing(true);
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    try {
      canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append("file", blob, "photo.jpg");

        const response = await fetch("/recognize-face", {
          method: "POST",
          body: formData,
        });
        const data = await response.json();
        setResult(data);
      }, "image/jpeg");
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-3xl font-medium tracking-tight">
            Photo Studio
          </h1>
          <p className="text-gray-400 mt-2">
            Capture moments with stunning filters
          </p>
        </header>

        {/* Main Content */}
        <div className="max-w-3xl mx-auto">
          {/* Camera View */}
          <div className="relative rounded-2xl overflow-hidden bg-gray-900 shadow-2xl">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-full object-cover"
            />
            <canvas
              ref={canvasRef}
              width="640"
              height="480"
              className="hidden"
            />

            {/* Filter Options */}
            <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex space-x-4">
              {['Original', 'Vivid', 'Noir'].map((filter) => (
                <button
                  key={filter}
                  className="px-4 py-2 rounded-full bg-white/10 backdrop-blur-md
                           hover:bg-white/20 transition-all duration-200"
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>

          {/* Controls */}
          <div className="mt-8 flex justify-center space-x-6">
            <button
              onClick={capturePhoto}
              disabled={isProcessing}
              className="flex items-center space-x-2 px-6 py-3 rounded-full
                       bg-white text-black font-medium hover:bg-gray-100
                       transition-all duration-200 disabled:opacity-50"
            >
              {isProcessing ? (
                <RefreshCw className="w-5 h-5 animate-spin" />
              ) : (
                <Camera className="w-5 h-5" />
              )}
              <span>{isProcessing ? 'Processing...' : 'Capture'}</span>
            </button>
          </div>

          {/* Result */}
          <Transition
            show={result != null}
            enter="transition-opacity duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="mt-8">
              {result?.image && (
                <div className="relative rounded-2xl overflow-hidden">
                  <img
                    src={`data:image/jpeg;base64,${result.image}`}
                    alt="Processed"
                    className="w-full"
                  />
                  <div className="absolute bottom-4 right-4 flex space-x-4">
                    <button className="p-2 rounded-full bg-white/10 backdrop-blur-md
                                     hover:bg-white/20 transition-all duration-200">
                      <Share2 className="w-5 h-5" />
                    </button>
                    <button className="p-2 rounded-full bg-white/10 backdrop-blur-md
                                     hover:bg-white/20 transition-all duration-200">
                      <Download className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </Transition>
        </div>
      </div>
    </div>
  );
}

export default App;