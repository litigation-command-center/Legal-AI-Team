// WebLLM Integration for Multi Agent Powerhouse
// Browser-based open source AI using WebGPU
// Supports Llama, Phi, Gemma, Mistral and more

class WebLLMAssistant {
    constructor() {
        this.initialized = false;
        this.loading = false;
        this.engine = null;
        this.model = 'Llama-3.1-8B-Instruct-q4f16_1-MLC';
        this.available = false;
    }

    async checkSupport() {
        // Check if WebGPU is available
        if (!navigator.gpu) {
            console.log('WebGPU not available');
            return false;
        }
        
        // Try to load WebLLM
        try {
            // Dynamic import from CDN
            const mlcAi = await import('https://esm.run/@mlc-ai/web-llm');
            this.MLCEngine = mlcAi.MLCEngine;
            this.available = true;
            console.log('WebLLM available');
            return true;
        } catch (e) {
            console.log('WebLLM not available:', e.message);
            return false;
        }
    }

    async initialize() {
        if (this.initialized || this.loading) return;
        
        this.loading = true;
        
        try {
            const supported = await this.checkSupport();
            if (!supported) {
                this.loading = false;
                return false;
            }
            
            console.log('Initializing WebLLM with model:', this.model);
            
            this.engine = new this.MLCEngine({
                model: this.model,
                device: 'gpu',
            });
            
            // Note: Model download happens on first use
            // This uses MLC's model cache
            await this.engine.reload();
            
            this.initialized = true;
            this.loading = false;
            console.log('WebLLM initialized successfully');
            return true;
        } catch (e) {
            console.error('WebLLM init failed:', e);
            this.loading = false;
            return false;
        }
    }

    async chat(messages, onChunk) {
        if (!this.initialized) {
            await this.initialize();
        }
        
        if (!this.initialized) {
            throw new Error('WebLLM not available');
        }

        // Convert messages to WebLLM format
        const formattedMessages = messages.map(m => ({
            role: m.role,
            content: m.content
        }));

        const chunks = [];
        await this.engine.chat.completions.create streamingReply(formattedMessages, {
            onChunk: (chunk) => {
                chunks.push(chunk);
                if (onChunk) onChunk(chunk.content);
            }
        });

        return chunks.map(c => c.content).join('');
    }

    async generate(prompt, onChunk) {
        if (!this.initialized) {
            await this.initialize();
        }
        
        if (!this.initialized) {
            throw new Error('WebLLM not available');
        }

        const chunks = [];
        await this.engine.chat.completions.create streamingReply([{
            role: 'user',
            content: prompt
        }], {
            onChunk: (chunk) => {
                chunks.push(chunk);
                if (onChunk) onChunk(chunk.content);
            }
        });

        return chunks.map(c => c.content).join('');
    }
}

// Fallback chain: WebLLM -> Mock
class LegalAssistant {
    constructor() {
        this.webllm = new WebLLMAssistant();
        this.useWebLLM = false;
        this.webllmChecked = false;
    }

    async checkCapabilities() {
        if (this.webllmChecked) return;
        
        this.webllmChecked = true;
        this.useWebLLM = await this.webllm.checkSupport();
        
        console.log('AI Capabilities:',
            this.useWebLLM ? 'WebLLM (local GPU)' : 'Mock (fallback)'
        );
    }

    async sendMessage(messages, onChunk) {
        await this.checkCapabilities();
        
        if (this.useWebLLM && this.webllm.initialized) {
            return await this.webllm.chat(messages, onChunk);
        }
        
        // Fallback to mock - handled by backend
        throw new Error('Use backend API');
    }
}

// Export for use
window.WebLLMAssistant = WebLLMAssistant;
window.LegalAssistant = LegalAssistant;