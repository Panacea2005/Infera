import React, { useState, useEffect, useRef } from 'react';
import { SkipBack, Play, Pause, SkipForward, RotateCcw, ZoomIn, ZoomOut } from 'lucide-react';



const DPLLViz = ({ result, knowledgeBase }) => {
    console.log('DPLLViz props:', { result, knowledgeBase });
    const [currentStep, setCurrentStep] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [speed, setSpeed] = useState(1000);
    const [zoomLevel, setZoomLevel] = useState(1);
    const svgRef = useRef(null);
  
    const parseDPLLData = (resultString) => {
      if (!resultString) return [];
  
      const steps = resultString.split('\n').filter(step => step.trim());
  
      return steps.map((step, index) => ({
        step: index + 1,
        detail: step.trim(),
        status: 'neutral' // Initialize all steps with a neutral status
      }));
    };
  
    const steps = parseDPLLData(result);
    console.log('Parsed DPLL steps:', steps);
  
    useEffect(() => {
      let timer;
      if (isPlaying && currentStep < steps.length - 1) {
        timer = setTimeout(() => {
          setCurrentStep(prev => prev + 1);
        }, speed);
      } else if (currentStep >= steps.length - 1) {
        setIsPlaying(false);
      }
      return () => clearTimeout(timer);
    }, [currentStep, isPlaying, steps.length, speed]);
  
    useEffect(() => {
      if (svgRef.current) {
        const currentNode = svgRef.current.querySelector(`#node-${currentStep}`);
        if (currentNode) {
          currentNode.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
        }
      }
    }, [currentStep]);
  
    const handlePlayPause = () => setIsPlaying(!isPlaying);
    const handleReset = () => {
      setCurrentStep(0);
      setIsPlaying(false);
    };
    const handleStepForward = () => {
      if (currentStep < steps.length - 1) setCurrentStep(currentStep + 1);
    };
    const handleStepBack = () => {
      if (currentStep > 0) setCurrentStep(currentStep - 1);
    };
  
    const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 0.1, 2));
    const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 0.1, 0.5));
  
    if (!steps.length) {
      console.log('No steps to display');
      return null;
    }
  
    const renderTreeNodes = (steps) => {
      const nodeWidth = 200;
      const nodeHeight = 80;
      const horizontalSpacing = 300;
      const verticalSpacing = 150;
      const totalLevels = Math.ceil(Math.log2(steps.length + 1));
      const svgWidth = (2 ** (totalLevels - 1)) * horizontalSpacing;
      const svgHeight = totalLevels * verticalSpacing + nodeHeight;
  
      const nodes = steps.map((step, index) => {
        const level = Math.floor(Math.log2(index + 1));
        const position = index - (2 ** level - 1);
        const x = (svgWidth / (2 ** (level + 1))) + position * (svgWidth / (2 ** level));
        const y = level * verticalSpacing + nodeHeight / 2;
        return { step, x, y };
      });
  
      return (
        <svg ref={svgRef} width={svgWidth} height={svgHeight} className="overflow-visible" style={{ transform: `scale(${zoomLevel})` }}>
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#3B82F6" />
            </marker>
          </defs>
          {nodes.map((node, index) => {
            if (index > 0) {
              const parentIndex = Math.floor((index - 1) / 2);
              const parent = nodes[parentIndex];
  
              return (
                <line
                  key={`line-${index}`}
                  x1={parent.x}
                  y1={parent.y}
                  x2={node.x}
                  y2={node.y}
                  stroke="#ccc"
                  strokeWidth={2}
                  markerEnd="url(#arrowhead)"
                />
              );
            }
            return null;
          })}
          {nodes.map((node, index) => (
            <g key={`node-${index}`} id={`node-${index}`} className="transition-all duration-500">
              <rect
                x={node.x - nodeWidth / 2}
                y={node.y - nodeHeight / 2}
                width={nodeWidth}
                height={nodeHeight}
                rx={15}
                ry={15}
                fill="#FFFFFF"
                stroke={
                  index === currentStep ? '#3B82F6' :
                  index < currentStep ? (steps[index].detail.includes('True') ? '#10B981' : (steps[index].detail.includes('False') ? '#EF4444' : '#3B82F6')) :
                  '#ccc'
                }
                strokeWidth={index === currentStep ? 3 : 2}
                className="transition-all duration-300"
              />
              <foreignObject
                x={node.x - nodeWidth / 2}
                y={node.y - nodeHeight / 2}
                width={nodeWidth}
                height={nodeHeight}
              >
                <div className="flex items-center justify-center h-full p-2">
                  <p className="text-sm font-mono text-gray-700 text-center break-words">{node.step.detail}</p>
                </div>
              </foreignObject>
            </g>
          ))}
        </svg>
      );
    };
  
    return (
      <div className="mt-8 bg-white rounded-lg p-6 shadow-lg">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">DPLL Visualization</h2>
          <p className="text-gray-800">Visualizing the DPLL algorithm steps.</p>
        </div>
  
        {/* Current Step Details */}
        <div className="bg-gray-50 rounded-lg p-6 mb-4">
          <h3 className="font-semibold text-gray-800 mb-4 text-lg">Step {currentStep + 1} Details</h3>
          <p className="text-gray-800">{steps[currentStep].detail}</p>
        </div>
  
        {/* Visualization Area */}
        <div className="relative bg-white rounded-lg mb-6 p-4 overflow-auto" style={{ width: '100%', height: '600px' }}>
          {renderTreeNodes(steps)}
        </div>
  
        {/* Controls */}
        <div className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-4">
            <button onClick={handleStepBack} disabled={currentStep === 0} className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed border-none text-gray-800">
              <SkipBack />
            </button>
            <button onClick={handlePlayPause} className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 border-none text-gray-800">
              {isPlaying ? <Pause /> : <Play />}
            </button>
            <button onClick={handleStepForward} disabled={currentStep === steps.length - 1} className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed border-none text-gray-800">
              <SkipForward />
            </button>
            <button onClick={handleReset} className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 border-none text-gray-800">
              <RotateCcw />
            </button>
            <button onClick={handleZoomIn} className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 border-none text-gray-800">
              <ZoomIn />
            </button>
            <button onClick={handleZoomOut} className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 border-none text-gray-800">
              <ZoomOut />
            </button>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-800">Speed:</span>
            <input type="range" min="200" max="2000" step="200" value={2000 - speed + 200} onChange={(e) => setSpeed(2000 - Number(e.target.value) + 200)} className="w-32" />
          </div>
          <div className="text-sm text-gray-800">Step {currentStep + 1} of {steps.length}</div>
        </div>
      </div>
    );
  };
  
  export default DPLLViz;