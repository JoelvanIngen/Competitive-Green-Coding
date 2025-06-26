"use client";

import React, { useRef, useState, useEffect, useActionState } from 'react';
import { submit, getResults, fetchResult } from './actions';

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"

import { Button } from "@/components/ui/button";

import Markdown from 'react-markdown';
import './markdown.css';
import hljs from 'highlight.js';
import './highlight.css';
import rehypeHighlight from 'rehype-highlight';

interface Props {
  data: {
    templateCode: string;
    difficulty: string;
    pid: string;
    name: string;
    language: string;
    tags: string[];
    longDesc: string;
    prevSubmission: boolean;
  },
  subData: {
    hastested: boolean;
    error: string;
    errormsg: string;
    testspassed: boolean;
    cputime: number;
    energyusage: number;
    emissions: number;
    submission: string;
    };
}


// Extend the Array interface globally
declare global {
  interface Array<T> {
    sample(): T;
  }
}

Array.prototype.sample = function(){
  return this[Math.floor(Math.random()*this.length)];
}

const resultMessages = {
    error: {
        src: 'images\\submission\\pass\\incognito\\full.png',
        messages: ['😬You weren’t supposed to see that.😬', 'Your results are missing... or it never existed. Either way, it\’s suspicious.'],
        color: 'text-theme-text'
    },
    prevsubmission: {
        src: 'images\\submission\\pass\\incognito\\full.png',
        messages: ['🕵️Back on the case.🕵️','Reopening the file. Let\’s see what you were working on...🗂️'],
        color: 'text-theme-text'
    },
    passed: [
        {
            src: 'images\\submission\\pass\\fire\\full.png',
            messages: [
                ['💥Unstoppable!💥', 'All tests passed! You\'re on fire - literally...'],
                ['🚀Code Deployed. Ego Boosted.🚀', 'You crushed it — not a single test stood a chance!'],
                ['🔥Certified Code Blazer.🔥', 'Tests passed like a hot knife through bugs!'],
                ['🧨Test Run: Obliterated🧨', 'Flawless victory! The fire is justified.']
            ].sample(),
            color: 'text-orange-700'
        },
        {
            src: 'images\\submission\\pass\\zen\\smooth.png',
            messages: [
                ['🎯No Bugs. No Strain. Just Precision.🎯', 'This is what coding enlightenment looks like.'],
                ['☁️Flawless Execution. Zero Resistance.☁️', 'Your logic is one with the universe.'],
                ['🧘All Tests Passed. Inner Peace Achieved.🧘', 'Your code flows like a tranquil river.'],
            ].sample(),
            color: 'text-teal-600'
        },
        {
            src: 'images\\submission\\fail\\frozen\\full.png',
            messages: [
                ['🧊Ice. In. Your. Veins.🧊', 'Every test passed with surgical precision. No mercy.'],
                ['🤖Zero emotion. Zero bugs.🤖', 'Passed. Silently. Efficiently. Like a coding machine.'],
                ['🥶Colder than a runtime warning.🥶', 'The tests didn\’t even stand a chance.'],
                ['❄️Frozen in success.❄️', 'That wasn\’t luck. That was calculated brilliance.']
            ].sample(),
            color: 'text-blue-400'
        }
        ],
    failed: {
        extinguished: {
            src: 'images\\submission\\fail\\extinguished\\smooth.png',
            messages: [
                ['Almost there!', 'Some tests didn\’t make it. But you\'re close - take another shot.🕯️'],
                ['Keep going!', 'A few bumps in the code, but nothing a little debugging can\’t fix.🧩'],
                ['Tests fought back.', 'And they won. But there\’s still time for revenge.⚔️'],
                ['Back to the drawing board.', 'The tests had questions your code couldn\’t answer - yet.✏️'],
                ['Still warming up.', 'The logic needs a little more spark to light the way.🔥'],
                ['Code cooling down.', 'A few tests slipped through the cracks. Let\’s patch it up.🧵']
            ].sample(),
            color: 'text-stone-400'
        },
        enraged: {
            src: 'images\\submission\\fail\\angry\\full.png',
            messages: [
                ['WHAT. WAS. THAT?', 'The code gods are displeased. Offer better syntax.👿'],
                ['Uncaught rage.', 'An error erupted before the tests even had a chance.👊'],
                ['You broke reality.', 'The interpreter is questioning its existence.🌀'],
                ['Critical meltdown!', 'Syntax chaos. The parser ran for its life.💥']
            ].sample(),
            color: 'text-gray-800'
        }        
    }
}

export default function Submission({ data, subData }: Props) {
    const panelLeft = useRef<any>(null);
    const panelRight = useRef<any>(null);
    const textarea = useRef<HTMLTextAreaElement>(null);
    const highlight = useRef<HTMLElement>(null);
    const lineNumbers = useRef<HTMLDivElement>(null);
    const scroll = useRef<HTMLDivElement>(null);

    const [code, setCode] = useState(data.templateCode);
    const [codeResults, formAction, isPending] = useActionState(submit, {status: 0, message: "", submissionuuid: 0});

    const [results, setResults] = useState(subData);

    const [seeResults, setSeeResults] = useState(false);
    const resultsVisible = seeResults ? '' : 'hidden';
    const resultsHidden = seeResults ? 'hidden' : '';
    
    const [tab, setTab] = useState("problem");
    const tabBtnProblem = tab === 'problem' ? '' : 'ghost';
    const tabProblem = tab === 'problem' ? '' : 'hidden';
    const tabBtnOutput = tab === 'output' ? '' : 'ghost';
    const tabOutput = tab === 'output' ? '' : 'hidden';

    const [resultPrompt, setResultPrompt] = useState(subData.submission ? resultMessages.prevsubmission : resultMessages.error);

    const [fetchingResults, setFetchingResults] = useState(false);
    const [fetchMessage, setFetchMessage] = useState("Submit your code to see results.");

    const difficultyStyle = data.difficulty === "easy" ? "bg-green-200 text-green-800"
                                                    : data.difficulty === "medium"
                                                    ? "bg-yellow-200 text-yellow-800"
                                                    : "bg-red-200 text-red-800"

    const [testResultsHeader, setTestResultsHeader] = useState(<p></p>);

    const [fetchingMessage, setFetchingMessage] = useState(['', '']);

    const parseCode = () => {
        return textarea.current?.value ?? "";
    }

    const highlightCode = () => {       
        const solution = parseCode();

        // if (textarea.current && scroll.current && highlight.current) {
        //     const lineHeight = parseFloat(window.getComputedStyle(textarea.current).lineHeight);
        //     const render_minlines = Math.max(0, Math.floor(scroll.current.scrollTop / lineHeight) - 3);
        //     const render_maxlines = Math.ceil((scroll.current.scrollTop + scroll.current.clientHeight) / lineHeight) + 3;

        //     const split = solution.split('\n');
        //     const pre_render = split.slice(0, render_minlines).join("\n");
        //     const render = split.slice(render_minlines, render_maxlines).join("\n");
        //     const post_render = split.slice(render_maxlines, split.length).join("\n");

        //     const highlighted = hljs.highlight(solution, {language: data.language}).value;

        //     highlight.current.innerHTML = (pre_render ? pre_render  + '\n': '') + highlighted + '\n' + post_render;
        // }

        if (textarea.current && highlight.current) {
            const highlighted = hljs.highlight(solution, {language: data.language}).value;
            highlight.current.innerHTML = highlighted;
        }

        setCode(solution);
        handleLineNumbers(solution);
        setSubmissionCookie(data.pid, parseCode());
    }

    const insertAtCaret = (str: string, moveCaret: number = 0) => {
        if (!textarea.current) return;
        const { value, selectionStart, selectionEnd } = textarea.current;
        textarea.current.value = `${value.substring(0, selectionEnd)}${str}${value.substring(selectionEnd)}`;
        textarea.current.selectionStart = textarea.current.selectionEnd = selectionStart + str.length - moveCaret;
    }

    const handleTab = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
        // Insert tabs
        if ((event.key) === 'Tab') {
            event.preventDefault();
            insertAtCaret('\t');    
        }
        // Automatic tabs when entering newline
        else if ((event.key) === 'Enter') {
            event.preventDefault();
            if (!textarea.current) return;
            var textLines = textarea.current.value.substr(0, textarea.current.selectionStart).split("\n");
            var currentLineNumber = textLines.length;
            var line = textLines[currentLineNumber-1] || "";
            const match = line.match(/^[ \t]*/);

            // Scroll down on newline
            if (textarea.current && scroll.current) {
                const lineHeight = parseFloat(window.getComputedStyle(textarea.current).lineHeight);
                scroll.current.scrollTop += lineHeight;
            }

            insertAtCaret('\n' + (match ? match[0] : ''));
        }
        // Bracket closing
        else if (['(', '{', '['].indexOf(event.key) > -1) {
            const pairs: { [key: string]: string } = {'(': ')', '{': '}', '[': ']'};
            event.preventDefault();
            insertAtCaret(event.key + pairs[event.key], 1);
        }
        highlightCode();
    }

    const handleSubmit = () => {
        setSeeResults(false);
        setFetchMessage('Submitting solution...');
        setTab('output');
        if (panelLeft.current) {
            panelLeft.current.expand();
            panelLeft.current.resize(50);
        }
        setFetchingResults(true);
    }

    const countLines = (str: string) => {
        if (str === '') return 0;
        return str.split('\n').length;
    }

    const handleLineNumbers = (solution: string) => {
        const lines = countLines(solution);

        if (!textarea.current || !lineNumbers.current) return;

        const lineHeight = parseFloat(window.getComputedStyle(textarea.current).lineHeight);
        const minLines = Math.floor(textarea.current.clientHeight / lineHeight) - 1;

        let spansHtml = '';
        for (let i = 1; i <= Math.max(lines, minLines); i++) {
            spansHtml += `<p>${i}</p>`;
        }
        lineNumbers.current.innerHTML = spansHtml;
    }

    function setSubmissionCookie(id: string, code: string) {
        const json = JSON.stringify({
            id: id,
            code: code
        });

        const name = "submission"

        const expires = new Date()
        expires.setDate(expires.getDate() + 1)
        document.cookie = `${name}=${json}; expires=${expires.toUTCString()}; path=/`
    }

    const cookieRegex = /submission=\{"id":"(\d+)","code":"(.*?)"\}/;

    const getCookie = () => {
        const cookie = document.cookie.match(cookieRegex);
        if (cookie === null) {
            return [null, '', ''];
        }
        return cookie;
    }

    // Syntax highlight on load
    useEffect(()=>{
        const cookie = getCookie();
        if (cookie[1] === data.pid) {
            console.log('found cookie', cookie[1], cookie[2]);
            if (textarea.current) {
                let code = cookie[2] ? cookie[2] : '';
                textarea.current.value = code.replace(/\\n/g, '\n').replace(/\\t/g, '\t');
            }
        }

        highlightCode();
        handleLineNumbers(parseCode());

    }, [])

    const loadSubmission = () => {
        if (textarea.current) {
            textarea.current.value = subData.submission;
            highlightCode();
            handleLineNumbers(parseCode());
            setSeeResults(true);
        }
    }

    useEffect(()=>{
        const cookie = getCookie();
        if (cookie[1] === data.pid) {
            console.log('found cookie', cookie[1], cookie[2]);
            if (textarea.current) {
                let code = cookie[2] ? cookie[2] : '';
                textarea.current.value = code.replace(/\\n/g, '\n').replace(/\\t/g, '\t');
            }     
        }
        highlightCode();
        handleLineNumbers(parseCode());
    }, [isPending])

    // Fetch code results if submission is successfull.
    useEffect( () => {
        async function loadResults() {
            console.log(codeResults);
            if (codeResults.status === 201) {
                setFetchingMessage(['Running your code...', 'This may take a while.']);

                const form = new FormData();
                form.append('submissionuuid', codeResults.submissionuuid);
                const result = await getResults(null, form);

                setResults(result)
                // console.log('error', results.error);
                console.log('checking:' , result);

                if (result.error === 'MISC') {
                    setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-red-800'>Something went wrong</span></p>);
                } else if (result.testspassed) {
                    // setResultPrompt(resultMessages.passed.sample());
                    setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-green-800'>✅Tests passed✅</span></p>);
                } else if (result.error !== 'tests_failed') {
                    // setResultPrompt(resultMessages.failed.enraged);
                    setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-red-800'>❌Compiler error❌</span></p>);
                } else {
                    // setResultPrompt(resultMessages.failed.extinguished);
                    setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-red-800'>❌Tests failed❌</span></p>);
                }
                setSeeResults(true);
            }
            setFetchingResults(false);
            setFetchingMessage(['','']);
        }
        loadResults();
    }, [codeResults])

    const handleToggle = (panel: string) => {
        const panelRef = panel == 'left' ? panelLeft : panelRight;
        if (panelRef.current) {
            if (panelRef.current.isCollapsed()) {
                panelRef.current.expand();
            } else {
                panelRef.current.collapse();
            }
        }
    }

    console.log(data);

    return (
        <form onSubmit={handleSubmit} action={formAction} className="h-[calc(100vh-82px)] flex flex-col ml-4 mr-4 overflow-hidden">
            <input type='hidden' name='problemId' defaultValue={data.pid}></input>
            <input type='hidden' name='language' defaultValue={data.language}></input>
            <div className="ml-8 mr-8 mt-2">
                <div>
                    <h1 className="text-theme-text font-bold text-2xl mb-2 inline">{data.name}</h1>
                    <p className={`${difficultyStyle} ml-6 w-fit inline-block pr-2 pl-2 text-center rounded-sm`}>{data.difficulty}</p>
                    <p className="ml-2 w-fit inline-block pr-2 pl-2 text-center bg-theme-text/10 rounded-sm">{data.language}</p>
                    {data.tags.map((tag, index)=>(<p key={index} className="ml-2 w-fit inline-block pr-2 pl-2 text-center bg-theme-text/10 rounded-sm">{tag}</p>))}
                </div>
                <div className="mt-2 mb-2">
                    <Button type='button' variant={tabBtnProblem || 'default'} className='outline-1 hover:outline-solid outline-theme-text' onClick={() => tab === 'problem' ? handleToggle('left') : setTab('problem')}>problem</Button>
                    <Button type='button' variant={tabBtnOutput || 'default'} className='ml-2 outline-1 hover:outline-solid outline-theme-text' onClick={() => tab === 'output' ? handleToggle('left') : setTab('output')}>output</Button>                
                    <Button className='float-right bg-theme-primary hover:bg-theme-primary-dark' type='submit' disabled={fetchingResults}>Run code</Button>
                    {subData.submission ? <Button variant='ghost' type='button' onClick={loadSubmission} className='outline-1 hover:outline-solid outline-theme-text float-right mr-4'>Get previous submission</Button>: <Button className='hidden' type='button'></Button>}
                </div>
            </div>
            <ResizablePanelGroup direction='horizontal' className='flex flex-col flex-1 min-h-0 mb-4'>
                <ResizablePanel collapsible ref={panelLeft} defaultSize={40} minSize={10}>
                    <div className="bg-card h-full mr-[3px] rounded-xl border shadow-sm overflow-y-auto min-scroll overflow-x-auto">
                        <div className='grid p-6'>
                            <div className={`markdown row-[1] col-[1] z-1 ${tabProblem}`}>
                                <Markdown rehypePlugins={[rehypeHighlight]}>{data.longDesc}</Markdown>
                            </div>
                            <div className={`row-[1] col-[1] ${tabOutput}`}>
                                <div className={resultsHidden}>
                                    <p className="text-transparent w-fit bg-clip-text animate-gradient font-bold bg-gradient-to-r from-theme-primary to-theme-text">{fetchMessage}</p>
                                    <p className='font-bold'>{codeResults.message}</p>
                                    <p className="text-transparent w-fit bg-clip-text animate-gradient font-bold bg-gradient-to-r from-theme-primary to-theme-text">{fetchingMessage[0]}</p>
                                    <p className='font-bold'>{fetchingMessage[1]}</p>
                                </div>
                                <div>
                                    <div className={`whitespace-nowrap ${resultsVisible}`}>
                                    {/* <div className={`whitespace-nowrap`}> */}
                                        {/* <div className='flex justify-center mb-4'>
                                            <div>
                                                <img className='max-h-[5em] max-w-[5em]' src={resultPrompt.src}></img>
                                            </div>
                                            <div>
                                                <h2 className='font-bold text-center text-3xl'>{resultPrompt.messages[0]}</h2>
                                                <h2 className='font-bold text-center text-2xl'>{resultPrompt.messages[1]}</h2>
                                            </div>
                                        </div> */}
                                        <div className='flex flex-wrap flex-[40%] justify-around mb-2'>
                                            <>{testResultsHeader}</>
                                            <p>    
                                                <span className='pl-4 pr-2 pb-4 text-center font-bold text-yellow-800'>⚡CPU time:</span> 
                                                <span>{results.cputime ? results.cputime.toFixed(5) : 0} ms</span>
                                            </p>
                                            <p>    
                                                <span className='pl-4 pr-2 pb-4 text-center font-bold text-green-800'>🔋Energy usage:</span> 
                                                <span>{results.energyusage ? (results.energyusage * 3600000).toFixed(5) : 0} Joule</span>
                                            </p>
                                            <p>    
                                                <span className='pl-4 pr-2 pb-4 text-center font-bold text-blue-800'>🌍Carbon emissions:</span> 
                                                <span>{results.emissions ? (results.emissions * 1000000).toFixed(5) : 0} mg CO₂</span>
                                            </p>
                                        </div>
                                        <p className='text-center text-xs border-b-1 border-theme-text'>    
                                                <span className='text-gray-500'><a href="https://codecarbon.io/">Measured using CodeCarbon</a></span>
                                        </p>
                                        <p className='mt-2'>    
                                            <span className='text-red-800 font-bold'>{results.error}{results.error ? ':' : ''}</span>
                                        </p>
                                        <span>{results.errormsg}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </ResizablePanel>
                <ResizableHandle withHandle className='bg-theme-bg'/>
                <ResizablePanel collapsible ref={panelRight} defaultSize={60} minSize={20}>
                    <div spellCheck="false" ref={scroll} className="min-scroll text-[0.8rem] h-full grid grid-cols-[3rem_1fr] bg-card ml-[3px] rounded-xl border shadow-sm overflow-x-auto overflow-y-auto">
                        <div ref={lineNumbers} className='row[1] col-[1] pl-4 pt-4 font-code text-left leading-relaxed whitespace-pre text-theme-text/50'>
                            <p>1</p><p>2</p>
                        </div>
                        <textarea name='code' ref={textarea} className="font-code resize-none overflow-hidden whitespace-pre text-transparent outline-none z-1 row-[1] col-[2] pt-4 pr-8 pb-8 leading-relaxed" style={{caretColor: "var(--theme-primary)"}} id="textare" onKeyDown={handleTab} onInput={highlightCode} defaultValue={data.templateCode}></textarea>
                        <pre className="row-[1] col-[2] pt-4 pr-8 pb-8 leading-relaxed">
                            <code ref={highlight} className="line-numbers font-code"></code>
                        </pre>
                    </div>
                </ResizablePanel>
            </ResizablePanelGroup>
        </form>
    );
}
