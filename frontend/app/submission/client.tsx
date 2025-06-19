"use client";

import React, { useRef, useState, useEffect, useActionState } from 'react';
import { submit, getResults } from './actions';

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

export default function Submission({ data }: Props) {
    const panelLeft = useRef(null);
    const panelRight = useRef(null);
    const textarea = useRef(null);
    const highlight = useRef(null);

    const [code, setCode] = useState(data.templateCode);

    const [codeResults, formAction, isPending] = useActionState(submit, {status: 0, message: "Submit your code to see results.", submissionuuid: 0});

    const [results, setResults] = useState({hastested: false, error: '', desc: '', testspassed: 0, testsfailed: 0, cputime: 0});
    const resultsVisible = results.hastested ? '' : 'hidden';
    const resultsHidden = results.hastested ? 'hidden' : '';

    const [tab, setTab] = useState("problem");
    const tabBtnProblem = tab === 'problem' ? '' : 'ghost';
    const tabProblem = tab === 'problem' ? '' : 'hidden';
    const tabBtnOutput = tab === 'output' ? '' : 'ghost';
    const tabOutput = tab === 'output' ? '' : 'hidden';
    

    const difficultyStyle = data.difficulty === "Easy" ? "bg-green-200 text-green-800"
                                                    : data.difficulty === "Medium"
                                                    ? "bg-yellow-200 text-yellow-800"
                                                    : "bg-red-200 text-red-800"

    const parseCode = () => {
        return textarea.current.value ?? "";
    }

    const highlightCode = () => {
        const highlighted = hljs.highlight(parseCode(), {language: 'python'}).value;
        highlight.current.innerHTML = highlighted;
        setCode(parseCode());
    }

    const handleTab = (event) => {
        if ((event.key) === 'Tab') {
            event.preventDefault();
            const area = textarea.current;
            const { value, selectionStart, selectionEnd } = area;
            textarea.current.value = `${value.substring(0, selectionEnd)}\t${value.substring(selectionEnd)}`;
            textarea.current.selectionStart = area.selectionEnd = selectionStart + 1;
        }
    }

    // Syntax highlight on load
    useEffect(()=>{
        highlightCode();
    }, [])

    useEffect(()=>{
        textarea.current.value = code;
    }, [isPending])

    // Fetch code results if submission is successfull.
    useEffect( () => {
        async function loadResults() {
            if (codeResults.status == 200) {
                const form = new FormData();
                form.append('problemId', data.pid);

                const result = await getResults(null, form);
                setResults(result);
            }
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

    return (
        <form action={formAction} className="h-[calc(100vh-64px)] flex flex-col ml-4 mr-4 overflow-hidden">
            <input type='hidden' name='problemId' defaultValue={data.pid}></input>
            <div className="ml-8 mr-8">
                <div>
                    <h1 className="text-theme-text font-bold text-2xl mb-2 inline">{data.name}</h1>
                    <p className={`${difficultyStyle} ml-6 inline-block pr-2 pl-2 text-center rounded-sm`}>{data.difficulty}</p>
                    <p className="ml-2 inline-block pr-2 pl-2 text-center bg-theme-text/10 rounded-sm">{data.language}</p>
                    {data.tags.map((tag, index)=>(<p key={index} className="ml-2 inline-block pr-2 pl-2 text-center bg-theme-text/10 rounded-sm">{tag}</p>))}
                </div>
                <div className="mt-2 mb-2">
                    <Button type='button' variant={tabBtnProblem || 'default'} className='outline-1 hover:outline-solid outline-theme-text' onClick={() => tab === 'problem' ? handleToggle('left') : setTab('problem')}>problem</Button>
                    <Button type='button' variant={tabBtnOutput || 'default'} className='ml-2 outline-1 hover:outline-solid outline-theme-text' onClick={() => tab === 'output' ? handleToggle('left') : setTab('output')}>output</Button>                    
                    <Button className='float-right bg-theme-primary hover:bg-theme-primary-dark' type='submit' disabled={isPending}>{isPending ? 'Submitting code' : 'Run code'}</Button>
                </div>
            </div>
            <ResizablePanelGroup direction='horizontal' className='flex flex-col flex-1 min-h-0 mb-4'>
                <ResizablePanel collapsible ref={panelLeft} defaultSize={40}>
                    <div className="h-full bg-card mr-[3px] rounded-xl border shadow-sm overflow-y-auto min-scroll overflow-x-auto">
                        <div className='grid p-8'>
                            <div className={`markdown row-[1] col-[1] z-1 ${tabProblem}`}>
                                <Markdown rehypePlugins={[rehypeHighlight]}>{data.longDesc}</Markdown>
                            </div>
                            <div className={`row-[1] col-[1] ${tabOutput}`}>
                                <div className={resultsHidden}>{codeResults.message}</div>
                                <div>
                                    <p className={`whitespace-nowrap ${resultsVisible}`}>
                                        <span className='font-bold'>CPU-Time:</span> {results.cputime}
                                        <span className='font-bold ml-4'>Tests passed:</span> {results.testspassed}
                                        <span className='font-bold ml-4'>Tests failed:</span> {results.testsfailed}
                                        <br/>
                                        <span>{results.desc}</span>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </ResizablePanel>
                <ResizableHandle className='invisible'/>
                <ResizablePanel collapsible ref={panelRight} defaultSize={60}>
                    <div spellCheck="false" className="min-scroll text-[0.8rem] h-full grid bg-card ml-[3px] rounded-xl border shadow-sm overflow-x-auto overflow-y-auto">
                        <textarea name='code' ref={textarea} className="font-code resize-none overflow-hidden whitespace-pre text-transparent outline-none z-1 row-[1] col-[1] p-8 leading-relaxed" style={{caretColor: "var(--theme-primary)"}} id="textare" onKeyDown={handleTab} onInput={highlightCode} defaultValue={data.templateCode}></textarea>
                        <pre className="row-[1] col-[1] p-8 leading-relaxed">
                            <code ref={highlight} className="line-numbers font-code"></code>
                        </pre>
                    </div>
                </ResizablePanel>   
            </ResizablePanelGroup>
        </form>
    );
}
