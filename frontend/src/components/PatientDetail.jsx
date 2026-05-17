import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function PatientDetail() {
  const { id } = useParams();
  const { token } = useAuth();
  const [patient, setPatient] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchPatient = async () => {
      try {
        const response = await fetch(`http://localhost:8000/patients/${id}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setPatient(data);
        }
      } catch (error) {
        console.error(error);
      }
    };

    if (token && id) {
      fetchPatient();
    }
  }, [token, id]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isStreaming) return;

    const userQuery = inputValue;
    setInputValue('');
    setIsStreaming(true);

    setMessages(prev => [...prev, { role: 'user', content: userQuery }]);
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query: userQuery })
      });

      if (!response.ok) throw new Error('Chat request failed');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data:')) {
            const dataText = line.replace(/^data:\s?/, '');
            
            if (dataText !== '[DONE]' && dataText.trim() !== '') {
              setMessages(prev => {
                const newMessages = [...prev];
                const lastIndex = newMessages.length - 1;
                newMessages[lastIndex] = {
                  ...newMessages[lastIndex],
                  content: newMessages[lastIndex].content + dataText
                };
                return newMessages;
              });
            }
          }
        }
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  if (!patient) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-8">
        <p className="text-xl text-gray-500">Loading patient data...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        <div className="flex justify-between items-center bg-white p-4 rounded-lg shadow-sm">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Patient: {patient.patient_id}</h1>
            <p className="text-sm text-gray-500">{patient.age} y/o | {patient.is_anomaly ? 'Anomaly Detected' : 'Clear'}</p>
          </div>
          <Link to="/dashboard" className="text-gray-600 hover:text-gray-900 border px-3 py-1 rounded">
            &larr; Back to Dashboard
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm h-full">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Telemetry Vitals</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 rounded border">
                <p className="text-sm text-gray-500">Resting BP</p>
                <p className="text-2xl font-bold text-red-600">{patient.vitals.resting_blood_pressure}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded border">
                <p className="text-sm text-gray-500">Max Heart Rate</p>
                <p className="text-2xl font-bold text-red-600">{patient.vitals.max_heart_rate}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded border">
                <p className="text-sm text-gray-500">Serum Cholestrol</p>
                <p className="text-2xl font-bold text-gray-900">{patient.vitals.serum_cholestrol}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded border">
                <p className="text-sm text-gray-500">ST Depression</p>
                <p className="text-2xl font-bold text-yellow-600">{patient.vitals.st_depression_induced}</p>
              </div>
            </div>
          </div>

          <div className="bg-white flex flex-col rounded-lg shadow-sm h-[600px]">
            <div className="p-4 border-b bg-gray-50 rounded-t-lg">
              <h2 className="text-lg font-semibold text-gray-900">AI Triage Assistant (RAG)</h2>
            </div>
            
            <div className="flex-1 p-4 overflow-y-auto space-y-4">
              {messages.length === 0 && (
                <div className="text-center text-gray-500 mt-10">
                  Ask a question about this patient's telemetry or history.
                </div>
              )}
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`rounded-lg py-2 px-4 max-w-[80%] ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t">
              <div className="flex space-x-2">
                <input 
                  type="text" 
                  placeholder="Ask about this patient's telemetry..." 
                  className="flex-1 border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={isStreaming}
                />
                <button 
                  onClick={handleSendMessage}
                  disabled={isStreaming || !inputValue.trim()}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 disabled:opacity-50"
                >
                  {isStreaming ? 'Thinking...' : 'Send'}
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}