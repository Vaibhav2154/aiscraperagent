'use client';

import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  UserGroupIcon, 
  BuildingOfficeIcon, 
  ChatBubbleLeftRightIcon,
  PlayIcon,
  MagnifyingGlassIcon,
  EyeIcon
} from '../components/icons';
import { 
  researchService, 
  agentService, 
  searchService, 
  chatService,
  CompanyProfile,
  LeadProfile,
  AgentStatus,
  ResearchSummary
} from '../lib/api';

export default function Dashboard() {
  const [summary, setSummary] = useState<ResearchSummary>({
    total_companies: 0,
    total_leads: 0,
    companies: [],
    embedding_stats: undefined
  });
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [researchQuery, setResearchQuery] = useState('');
  const [chatQuery, setChatQuery] = useState('');
  const [chatResponse, setChatResponse] = useState('');
  const [chatSources, setChatSources] = useState<string[]>([]);
  const [researchLoading, setResearchLoading] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    loadDashboardData();
    // Poll for agent status updates every 5 seconds
    const interval = setInterval(loadAgentStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [summaryRes, agentRes] = await Promise.all([
        searchService.getSummary(),
        agentService.getStatus()
      ]);
      
      setSummary(summaryRes.data);
      setAgents(agentRes.data.agents || []);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAgentStatus = async () => {
    try {
      const response = await agentService.getStatus();
      setAgents(response.data.agents || []);
      setSummary(response.data.summary);
    } catch (error) {
      console.error('Error loading agent status:', error);
    }
  };

  const handleLaunchResearch = async () => {
    if (!researchQuery.trim()) return;
    
    try {
      setResearchLoading(true);
      await researchService.launchResearch(researchQuery.trim(), 10);
      setResearchQuery('');
      // Refresh data after a short delay
      setTimeout(loadDashboardData, 1000);
    } catch (error) {
      console.error('Error launching research:', error);
    } finally {
      setResearchLoading(false);
    }
  };

  const handleChat = async () => {
    if (!chatQuery.trim()) return;
    
    try {
      setChatLoading(true);
      const response = await chatService.chat(chatQuery.trim());
      setChatResponse(response.data.answer);
      setChatSources(response.data.sources);
    } catch (error) {
      console.error('Error in chat:', error);
      setChatResponse('Sorry, I encountered an error while processing your question.');
      setChatSources([]);
    } finally {
      setChatLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
        <div className="text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-200 mx-auto"></div>
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-transparent border-t-indigo-600 mx-auto absolute top-0"></div>
          </div>
          <p className="mt-6 text-lg font-medium text-gray-700">Loading your intelligence dashboard...</p>
          <p className="mt-2 text-sm text-gray-500">Preparing multi-agent system</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-12 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 mb-6">
            <ChartBarIcon className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent mb-4">
            AI Lead Research Intelligence
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Harness the power of multi-agent AI to discover competitors, gather comprehensive lead data, 
            and unlock actionable intelligence through natural conversation
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="group bg-white/70 backdrop-blur-sm overflow-hidden shadow-lg rounded-2xl border border-white/20 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="p-8">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="p-3 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 group-hover:from-blue-600 group-hover:to-indigo-700 transition-all duration-300">
                    <BuildingOfficeIcon className="h-7 w-7 text-white" />
                  </div>
                </div>
                <div className="ml-6 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate mb-1">Companies Researched</dt>
                    <dd className="text-3xl font-bold text-gray-900">{summary.total_companies}</dd>
                    <dd className="text-xs text-blue-600 font-medium">+{summary.total_companies > 0 ? '12%' : '0%'} this week</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="group bg-white/70 backdrop-blur-sm overflow-hidden shadow-lg rounded-2xl border border-white/20 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="p-8">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="p-3 rounded-xl bg-gradient-to-r from-emerald-500 to-green-600 group-hover:from-emerald-600 group-hover:to-green-700 transition-all duration-300">
                    <UserGroupIcon className="h-7 w-7 text-white" />
                  </div>
                </div>
                <div className="ml-6 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate mb-1">Leads Collected</dt>
                    <dd className="text-3xl font-bold text-gray-900">{summary.total_leads}</dd>
                    <dd className="text-xs text-emerald-600 font-medium">+{summary.total_leads > 0 ? '24%' : '0%'} this week</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="group bg-white/70 backdrop-blur-sm overflow-hidden shadow-lg rounded-2xl border border-white/20 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="p-8">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="p-3 rounded-xl bg-gradient-to-r from-amber-500 to-orange-600 group-hover:from-amber-600 group-hover:to-orange-700 transition-all duration-300">
                    <ChartBarIcon className="h-7 w-7 text-white" />
                  </div>
                </div>
                <div className="ml-6 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate mb-1">Active Agents</dt>
                    <dd className="text-3xl font-bold text-gray-900">
                      {agents.filter(a => a.status === 'running').length}
                    </dd>
                    <dd className="text-xs text-amber-600 font-medium">
                      {agents.length > 0 ? 'Processing now' : 'Ready to deploy'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="group bg-white/70 backdrop-blur-sm overflow-hidden shadow-lg rounded-2xl border border-white/20 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="p-8">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="p-3 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 group-hover:from-violet-600 group-hover:to-purple-700 transition-all duration-300">
                    <ChatBubbleLeftRightIcon className="h-7 w-7 text-white" />
                  </div>
                </div>
                <div className="ml-6 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate mb-1">Intelligence Docs</dt>
                    <dd className="text-3xl font-bold text-gray-900">{summary.embedding_stats?.total_documents || 0}</dd>
                    <dd className="text-xs text-violet-600 font-medium">Ready for queries</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Research Panel */}
          <div className="bg-white/80 backdrop-blur-sm shadow-xl rounded-3xl border border-white/20 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 px-8 py-6">
              <div className="flex items-center">
                <div className="p-2 bg-white/20 rounded-xl mr-4">
                  <MagnifyingGlassIcon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Launch Research Mission</h3>
                  <p className="text-indigo-100 text-sm">Deploy AI agents to discover competitors and gather intelligence</p>
                </div>
              </div>
            </div>
            <div className="p-8">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Target Company</label>
                  <input
                    type="text"
                    placeholder="e.g., Apollo, Lemlist, HubSpot, Salesforce..."
                    value={researchQuery}
                    onChange={(e) => setResearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleLaunchResearch()}
                    className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-300"
                    disabled={researchLoading}
                  />
                </div>
                <button
                  onClick={handleLaunchResearch}
                  disabled={researchLoading || !researchQuery.trim()}
                  className="w-full inline-flex items-center justify-center px-6 py-4 border border-transparent text-base font-semibold rounded-xl shadow-lg text-white bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 disabled:hover:scale-100"
                >
                  {researchLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-3"></div>
                      Deploying Agents...
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-5 w-5 mr-3" />
                      Launch Multi-Agent Research
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Chat Panel */}
          <div className="bg-white/80 backdrop-blur-sm shadow-xl rounded-3xl border border-white/20 overflow-hidden">
            <div className="bg-gradient-to-r from-emerald-500 to-teal-600 px-8 py-6">
              <div className="flex items-center">
                <div className="p-2 bg-white/20 rounded-xl mr-4">
                  <ChatBubbleLeftRightIcon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Intelligence Chat</h3>
                  <p className="text-emerald-100 text-sm">Query your collected data using natural language</p>
                </div>
              </div>
            </div>
            <div className="p-8">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Ask Anything</label>
                  <input
                    type="text"
                    placeholder="e.g., How many SDRs work at Apollo? Which companies raised funding?"
                    value={chatQuery}
                    onChange={(e) => setChatQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleChat()}
                    className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all duration-300"
                    disabled={chatLoading}
                  />
                </div>
                <button
                  onClick={handleChat}
                  disabled={chatLoading || !chatQuery.trim()}
                  className="w-full inline-flex items-center justify-center px-6 py-4 border border-transparent text-base font-semibold rounded-xl shadow-lg text-white bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 disabled:hover:scale-100"
                >
                  {chatLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-3"></div>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <ChatBubbleLeftRightIcon className="h-5 w-5 mr-3" />
                      Ask Intelligence
                    </>
                  )}
                </button>
              </div>
              
              {chatResponse && (
                <div className="mt-6 p-6 bg-gradient-to-br from-gray-50 to-emerald-50 rounded-2xl border-2 border-emerald-100">
                  <div className="flex items-start space-x-3">
                    <div className="p-2 bg-emerald-100 rounded-lg">
                      <ChatBubbleLeftRightIcon className="h-5 w-5 text-emerald-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-900 font-medium leading-relaxed">{chatResponse}</p>
                      {chatSources.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-emerald-200">
                          <p className="text-xs font-semibold text-emerald-700 mb-2">Intelligence Sources:</p>
                          <ul className="space-y-1">
                            {chatSources.map((source, index) => (
                              <li key={index} className="text-xs text-emerald-600 flex items-center">
                                <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full mr-2"></div>
                                {source}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Agent Status */}
        {agents.length > 0 && (
          <div className="mb-12 bg-white/80 backdrop-blur-sm shadow-xl rounded-3xl border border-white/20 overflow-hidden">
            <div className="bg-gradient-to-r from-amber-500 to-orange-600 px-8 py-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="p-2 bg-white/20 rounded-xl mr-4">
                    <ChartBarIcon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">Agent Command Center</h3>
                    <p className="text-amber-100 text-sm">Real-time monitoring of AI research agents</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-white">{agents.length}</div>
                  <div className="text-amber-100 text-xs">Active Missions</div>
                </div>
              </div>
            </div>
            <div className="p-8">
              <div className="space-y-4">
                {agents.map((agent) => (
                  <div key={agent.agent_id} className="group relative overflow-hidden rounded-2xl border-2 border-gray-100 bg-white p-6 hover:border-amber-200 transition-all duration-300">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h4 className="font-bold text-gray-900 text-lg">{agent.company}</h4>
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(agent.status)}`}>
                            <div className={`w-2 h-2 rounded-full mr-2 ${
                              agent.status === 'running' ? 'bg-amber-500 animate-pulse' :
                              agent.status === 'completed' ? 'bg-emerald-500' : 'bg-red-500'
                            }`}></div>
                            {agent.status.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-gray-600 text-sm mb-3">{agent.message}</p>
                        <div className="flex items-center space-x-4">
                          <div className="flex-1">
                            <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                              <span>Progress</span>
                              <span>{agent.progress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                              <div 
                                className={`h-2 rounded-full transition-all duration-500 ${
                                  agent.status === 'completed' ? 'bg-gradient-to-r from-emerald-500 to-green-500' :
                                  agent.status === 'running' ? 'bg-gradient-to-r from-amber-500 to-orange-500' :
                                  'bg-gradient-to-r from-red-500 to-rose-500'
                                }`}
                                style={{ width: `${agent.progress}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Companies Overview */}
        {summary.companies && summary.companies.length > 0 && (
          <div className="bg-white/80 backdrop-blur-sm shadow-xl rounded-3xl border border-white/20 overflow-hidden">
            <div className="bg-gradient-to-r from-violet-500 to-purple-600 px-8 py-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="p-2 bg-white/20 rounded-xl mr-4">
                    <BuildingOfficeIcon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">Intelligence Portfolio</h3>
                    <p className="text-violet-100 text-sm">Comprehensive overview of researched companies</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-white">{summary.companies?.length || 0}</div>
                  <div className="text-violet-100 text-xs">Companies</div>
                </div>
              </div>
            </div>
            <div className="p-8">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {(summary.companies || []).map((company, index) => (
                  <div key={index} className="group relative overflow-hidden rounded-2xl bg-white border-2 border-gray-100 p-6 hover:border-violet-200 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                    <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-violet-500/10 to-purple-600/10 rounded-bl-2xl"></div>
                    <div className="relative">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-bold text-gray-900 text-lg group-hover:text-violet-600 transition-colors duration-300">
                          {company.name}
                        </h4>
                        <div className="w-3 h-3 bg-gradient-to-r from-violet-500 to-purple-600 rounded-full"></div>
                      </div>
                      
                      <div className="space-y-3">
                        {company.industry && (
                          <div className="flex items-center text-sm">
                            <span className="w-2 h-2 bg-violet-400 rounded-full mr-3"></span>
                            <span className="text-gray-600 font-medium">Industry:</span>
                            <span className="text-gray-900 ml-2">{company.industry}</span>
                          </div>
                        )}
                        
                        {company.location && (
                          <div className="flex items-center text-sm">
                            <span className="w-2 h-2 bg-purple-400 rounded-full mr-3"></span>
                            <span className="text-gray-600 font-medium">Location:</span>
                            <span className="text-gray-900 ml-2">{company.location}</span>
                          </div>
                        )}
                        
                        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                          <div className="flex items-center text-sm">
                            <UserGroupIcon className="h-4 w-4 text-violet-500 mr-2" />
                            <span className="text-gray-600 font-medium">{company.leads_count} leads</span>
                          </div>
                          <div className="px-3 py-1 bg-gradient-to-r from-violet-100 to-purple-100 text-violet-700 text-xs font-semibold rounded-full">
                            Analyzed
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
