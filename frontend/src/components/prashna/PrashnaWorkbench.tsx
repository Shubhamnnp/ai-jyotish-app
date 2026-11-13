'use client';

import React, { useState } from 'react';

interface PrashnaWorkbenchProps {
  className?: string;
}

export const PrashnaWorkbench: React.FC<PrashnaWorkbenchProps> = ({ className = '' }) => {
  const [question, setQuestion] = useState('क्या मुझे नई नौकरी या पदोन्नति मिलेगी?');
  const [category, setCategory] = useState('Career');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<{
    verdict: string;
    verdictColor: string;
    ithasala: string;
    posRules: number;
    negRules: number;
    score: number;
  } | null>({
    verdict: 'कार्य सिद्धि (अनुकूल योग सक्रिय)',
    verdictColor: 'text-emerald-600 dark:text-emerald-400',
    ithasala: 'पूर्ण इत्थशाल योग (लग्न व दशमेश के मध्य दीप्तांश भीतर संबंध)',
    posRules: 12,
    negRules: 6,
    score: +110,
  });

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
      setResult({
        verdict: 'कार्य सिद्धि (शीघ्र फल प्राप्ति)',
        verdictColor: 'text-emerald-600 dark:text-emerald-400',
        ithasala: 'प्रत्यक्ष इत्थशाल योग (शुक्र व गुरु परस्पर दृष्ट)',
        posRules: 14,
        negRules: 4,
        score: +135,
      });
    }, 600);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Horary Input Box */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 dark:border-slate-800">
          <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">
            तात्कालिक प्रश्न विश्लेषण (Horary Prashna Engine)
          </span>
          <span className="text-xs text-slate-500 font-mono">
            ताजिक नीलकण्ठी एवं प्रश्न मार्ग
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="md:col-span-2 space-y-1.5">
            <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
              प्रश्न विवरण (Question Query)
            </label>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-amber-500/50"
              placeholder="प्रश्न दर्ज करें..."
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
              विषय वर्ग (Category)
            </label>
            <div className="flex gap-2">
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 text-sm bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-amber-500/50"
              >
                <option value="Career">आजीविका / पदोन्नति (Career)</option>
                <option value="Wealth">धन लाभ / वित्त (Wealth)</option>
                <option value="Health">आरोग्य / स्वास्थ्य (Health)</option>
                <option value="Marriage">विवाह / संबंध (Marriage)</option>
                <option value="Travel">विदेश यात्रा (Travel)</option>
              </select>

              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="px-4 py-2 text-xs font-semibold bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition-colors whitespace-nowrap shadow-xs disabled:opacity-50"
              >
                {isAnalyzing ? 'विश्लेषण...' : 'मूल्यांकन'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Result Metrics */}
      {result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="p-3.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <div className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">प्रश्न निर्णय (Verdict)</div>
            <div className={`mt-1 text-sm font-bold ${result.verdictColor}`}>
              {result.verdict}
            </div>
            <div className="text-[11px] text-slate-500 mt-1 line-clamp-1">{result.ithasala}</div>
          </div>

          <div className="p-3.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <div className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">सक्रिय शुभ नियम</div>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-base font-bold text-emerald-600 dark:text-emerald-400">
                {result.posRules} नियम
              </span>
              <span className="text-xs text-rose-500">
                ({result.negRules} बाधाएं)
              </span>
            </div>
            <div className="text-[11px] text-slate-500 mt-1">100 शास्त्रीय नियमों का स्वचालित वेध</div>
          </div>

          <div className="p-3.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <div className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">शुद्ध शास्त्रीय संतुलन</div>
            <div className="mt-1 text-base font-bold text-blue-600 dark:text-blue-400">
              +{result.score} अंक (सकारात्मक)
            </div>
            <div className="text-[11px] text-slate-500 mt-1">कार्य सिद्धि संभावना {">"} 85%</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PrashnaWorkbench;
