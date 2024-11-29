import React, { useState, useEffect } from 'react';
import { Play, Pause, SkipBack, SkipForward, RotateCcw } from 'lucide-react';

const ChainViz = ({ type, result, knowledgeBase }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [visibleNodes, setVisibleNodes] = useState(1);
  const [speed, setSpeed] = useState(1000);
  const [isPlaying, setIsPlaying] = useState(false);

  // Enhanced parsing to handle Horn KB format
  const parseChainData = (resultString, kb) => {
    if (!resultString.includes('YES:')) {
      return [];
    }

    const facts = resultString.split('YES:')[1].trim().split(', ');
    const steps = [];
    const kbStructure = parseHornKB(kb);

    if (type === 'FC') {
      // For Forward Chaining
      let knownFacts = new Set();
      facts.forEach((fact, index) => {
        const currentFact = fact.trim();
        const previousFacts = [...knownFacts];

        // Find which rule(s) led to this fact
        const applicableRules = findApplicableRules(currentFact, previousFacts, kbStructure);

        // Determine reasoning based on whether it's initial fact or derived
        const reasoning = kbStructure.initialFacts.includes(currentFact)
          ? {
            type: 'initial',
            explanation: "Initial fact from knowledge base",
            usedRule: null,
            prerequisites: []
          }
          : {
            type: 'derived',
            explanation: `Derived using rule: ${applicableRules.rule}`,
            usedRule: applicableRules.rule,
            prerequisites: applicableRules.prerequisites
          };

        steps.push({
          fact: currentFact,
          knownFacts: [...previousFacts],
          reasoning,
          type: kbStructure.initialFacts.includes(currentFact) ? 'initial' : 'derived'
        });

        knownFacts.add(currentFact);
      });
    } else {
      // For Backward Chaining
      facts.reverse().forEach((fact, index) => {
        const currentFact = fact.trim();
        const nextFact = index < facts.length - 1 ? facts[index + 1].trim() : null;

        // Find which rule led to this fact in backward chaining
        const applicableRule = findBackwardRule(currentFact, nextFact, kbStructure);

        steps.push({
          fact: currentFact,
          subgoals: index < facts.length - 1 ? [facts[index + 1].trim()] : [],
          reasoning: {
            type: index === 0 ? 'goal' : index === facts.length - 1 ? 'base' : 'support',
            explanation: index === 0
              ? "Goal to prove"
              : index === facts.length - 1
                ? "Base fact from knowledge base"
                : `Using rule: ${applicableRule}`,
            usedRule: applicableRule,
            prerequisites: index < facts.length - 1 ? [facts[index + 1].trim()] : []
          },
          type: index === 0 ? 'goal' : index === facts.length - 1 ? 'base' : 'support'
        });
      });
    }

    return steps;
  };

  // Helper function to parse Horn KB format
  const parseHornKB = (kb) => {
    if (!kb) return { rules: [], initialFacts: [] };

    const lines = kb.split('\n');
    const rules = [];
    const initialFacts = [];

    let isTell = false;
    let isAsk = false;

    lines.forEach(line => {
      if (line.trim() === 'TELL') {
        isTell = true;
        return;
      }
      if (line.trim() === 'ASK') {
        isTell = false;
        isAsk = true;
        return;
      }

      if (isTell) {
        // Split the line by semicolons to get individual statements
        const statements = line.split(';').map(s => s.trim()).filter(s => s);

        statements.forEach(statement => {
          if (statement.includes('=>')) {
            // This is a rule
            const [antecedent, consequent] = statement.split('=>').map(s => s.trim());
            const prerequisites = antecedent.split('&').map(s => s.trim());
            rules.push({
              antecedent: prerequisites,
              consequent: consequent,
              original: statement
            });
          } else if (statement) {
            // This is an initial fact
            initialFacts.push(statement);
          }
        });
      }
    });

    return { rules, initialFacts };
  };

  // Helper function to find which rules led to a fact
  const findApplicableRules = (fact, knownFacts, kbStructure) => {
    const applicable = kbStructure.rules.find(rule =>
      rule.consequent === fact &&
      rule.antecedent.every(prereq => knownFacts.includes(prereq))
    );

    if (applicable) {
      return {
        rule: applicable.original,
        prerequisites: applicable.antecedent
      };
    }

    return {
      rule: "Direct fact",
      prerequisites: []
    };
  };

  // Helper function to find backward chaining rule
  const findBackwardRule = (current, next, kbStructure) => {
    if (!next) return "Base fact";

    const rule = kbStructure.rules.find(r =>
      r.consequent === current &&
      r.antecedent.includes(next)
    );

    return rule ? rule.original : "Direct implication";
  };

  const steps = parseChainData(result, knowledgeBase);

  // Enhanced Current Step Details Section
  const renderStepDetails = () => {
    if (currentStep >= steps.length) return null;

    const step = steps[currentStep];
    const reasoning = step.reasoning;

    return (
      <div className="bg-blue-50 rounded-lg p-6 mb-4">
        <h3 className="font-semibold text-blue-800 mb-4 text-lg">Step {currentStep + 1} Details</h3>

        <div className="space-y-4">
          {/* Current Fact */}
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <h4 className="font-medium text-blue-700 mb-2">Current Fact</h4>
            <p className="text-gray-800 font-mono">{step.fact}</p>
          </div>

          {/* Reasoning Process */}
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <h4 className="font-medium text-blue-700 mb-2">Reasoning Process</h4>
            <div className="space-y-2">
              <p className="text-gray-800">
                <span className="font-medium">Type:</span> {reasoning.type}
              </p>
              <p className="text-gray-800">
                <span className="font-medium">Explanation:</span> {reasoning.explanation}
              </p>
              {reasoning.usedRule && (
                <p className="text-gray-800">
                  <span className="font-medium">Applied Rule:</span>
                  <code className="ml-2 p-1 bg-gray-100 rounded font-mono">
                    {reasoning.usedRule}
                  </code>
                </p>
              )}
            </div>
          </div>

          {/* Prerequisites/Known Facts */}
          {type === 'FC' && step.knownFacts.length > 0 && (
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <h4 className="font-medium text-blue-700 mb-2">Known Facts</h4>
              <p className="text-gray-800 font-mono">
                {step.knownFacts.join(', ')}
              </p>
            </div>
          )}


          {/* Supporting Facts for BC */}
          {type === 'BC' && step.subgoals.length > 0 && (
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <h4 className="font-medium text-blue-700 mb-2">Supporting Facts Needed</h4>
              <ul className="list-disc list-inside space-y-1">
                {step.subgoals.map((fact, idx) => (
                  <li key={idx} className="text-gray-800 font-mono">{fact}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    );
  };

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

  if (!steps.length) return null;

  const renderNodes = () => {
    const nodeRadius = 40;
    const svgWidth = 800;
    const svgHeight = 400;
    const centerY = svgHeight / 2;
    const horizontalSpacing = (svgWidth - 100) / (steps.length > 1 ? steps.length - 1 : 1);

    // Effect to handle node appearance during play
    useEffect(() => {
      let timer;
      if (isPlaying && visibleNodes < steps.length) {
        timer = setTimeout(() => {
          setVisibleNodes(prev => Math.min(prev + 1, steps.length));
        }, speed / 2); // Make nodes appear faster than the step progression
      }
      return () => clearTimeout(timer);
    }, [isPlaying, visibleNodes, steps.length, speed]);

    // Reset visible nodes when resetting animation
    useEffect(() => {
      if (currentStep === 0 && !isPlaying) {
        setVisibleNodes(1);
      }
    }, [currentStep, isPlaying]);

    // Update visible nodes when stepping manually
    useEffect(() => {
      setVisibleNodes(prev => Math.max(prev, currentStep + 1));
    }, [currentStep]);

    return (
      <svg
        width="100%"
        height={svgHeight}
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        className="overflow-visible"
      >
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon
              points="0 0, 10 3.5, 0 7"
              fill="#3B82F6"
              className="transition-all duration-500"
            />
          </marker>

          {/* Gradient definitions for modern look */}
          <linearGradient id="activeGlow" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#93C5FD" />
            <stop offset="100%" stopColor="#3B82F6" />
          </linearGradient>

          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Connection lines with arrows */}
        {steps.map((step, index) => {
          if (index < steps.length - 1 && index < visibleNodes - 1) {
            const x1 = 50 + index * horizontalSpacing + nodeRadius;
            const x2 = 50 + (index + 1) * horizontalSpacing - nodeRadius;
            const y = centerY;

            return (
              <g key={`connection-${index}`}>
                {/* Shadow line */}
                <line
                  x1={x1}
                  y1={y}
                  x2={x2}
                  y2={y}
                  stroke="#E2E8F0"
                  strokeWidth={6}
                  className="transition-all duration-500"
                />
                {/* Main line */}
                <line
                  x1={x1}
                  y1={y}
                  x2={x2}
                  y2={y}
                  stroke={index <= currentStep - 1 ? '#3B82F6' : '#CBD5E1'}
                  strokeWidth={3}
                  markerEnd="url(#arrowhead)"
                  className="transition-all duration-500"
                  strokeDasharray="8,4"
                />
              </g>
            );
          }
          return null;
        })}

        {/* Nodes */}
        {steps.map((step, index) => {
          if (index >= visibleNodes) return null;

          const x = 50 + index * horizontalSpacing;
          const y = centerY;
          const isActive = index === currentStep;
          const isCompleted = index < currentStep;

          // Always keep background light for better text readability
          const fillColor = '#FFFFFF';
          let strokeColor = '#E2E8F0'; // Default
          let strokeWidth = 2;
          let glowEffect = '';

          if (isActive) {
            strokeColor = '#3B82F6';
            strokeWidth = 3;
            glowEffect = 'filter: url(#glow)';
          } else if (isCompleted) {
            strokeColor = '#10B981';
            strokeWidth = 3;
          }

          return (
            <g
              key={`node-${index}`}
              className="transition-all duration-500"
              style={{
                opacity: index < visibleNodes ? 1 : 0,
                transform: `scale(${index < visibleNodes ? 1 : 0})`,
                transformOrigin: `${x}px ${y}px`
              }}
            >
              {/* Node circle with shadow */}
              <circle
                cx={x}
                cy={y}
                r={nodeRadius + 2}
                fill="#F8FAFC"
                className="transition-all duration-300"
              />
              {/* Main node circle */}
              <circle
                cx={x}
                cy={y}
                r={nodeRadius}
                fill={fillColor}
                stroke={strokeColor}
                strokeWidth={strokeWidth}
                className="transition-all duration-300"
                style={{ glowEffect }}
              />

              {/* Step number */}
              <text
                x={x}
                y={y - 20}
                textAnchor="middle"
                className={`text-sm font-semibold ${isActive ? 'fill-blue-600' :
                    isCompleted ? 'fill-green-600' :
                      'fill-gray-400'
                  }`}
              >
                Step {index + 1}
              </text>

              {/* Fact text - always dark for readability */}
              <text
                x={x}
                y={y + 5}
                textAnchor="middle"
                className="text-sm font-mono fill-gray-700"
              >
                {step.fact}
              </text>

              {/* Type indicator */}
              <text
                x={x}
                y={y + 25}
                textAnchor="middle"
                className="text-xs fill-gray-500"
              >
                {step.type}
              </text>
            </g>
          );
        })}
      </svg>
    );
  };

  return (
    <div className="mt-8 bg-white rounded-lg p-6 shadow-lg">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-2">
          {type === 'FC' ? 'Forward' : 'Backward'} Chaining Visualization
        </h2>
        <p className="text-gray-600">
          {type === 'FC'
            ? 'Starting from known facts, deriving new facts until the goal is reached'
            : 'Starting from the goal, working backwards to find supporting facts'}
        </p>
      </div>

      {/* Current Step Details */}
      {renderStepDetails()}

      {/* Visualization Area */}
      <div className="relative bg-white rounded-lg mb-6">
        {renderNodes()}
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-4">
            <button
              onClick={handleStepBack}
              disabled={currentStep === 0}
              className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed border-none"
            >
              <SkipBack className="w-5 h-5 text-black" />
            </button>
            <button
              onClick={handlePlayPause}
              className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 border-none"
            >
              {isPlaying ? <Pause className="w-5 h-5 text-black" /> : <Play className="w-5 h-5 text-black" />}
            </button>
            <button
              onClick={handleStepForward}
              disabled={currentStep === steps.length - 1}
              className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed border-none"
            >
              <SkipForward className="w-5 h-5 text-black" />
            </button>
            <button
              onClick={handleReset}
              className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 border-none"
            >
              <RotateCcw className="w-5 h-5 text-black" />
            </button>
          </div>
        </div>

        {/* Playback Speed Control */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Speed:</span>
          <input
            type="range"
            min="200"
            max="2000"
            step="200"
            value={2000 - speed + 200}
            onChange={(e) => setSpeed(2000 - Number(e.target.value) + 200)}
            className="w-32"
          />
        </div>

        <div className="text-sm text-gray-600">
          Step {currentStep + 1} of {steps.length}
        </div>
      </div>
    </div>
  );
};

export default ChainViz;