#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import fetch from 'node-fetch';

// Asset metadata URL
const METADATA_URL = 'https://raw.githubusercontent.com/b-ciq/brand-assets/main/metadata/asset-inventory.json';

class CIQBrandAssetsServer {
  constructor() {
    this.server = new Server(
      {
        name: 'ciq-brand-assets',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.assetData = null;
    this.conversationState = new Map();
    
    this.setupTools();
    this.loadAssetData();
  }

  async loadAssetData() {
    try {
      const response = await fetch(METADATA_URL);
      this.assetData = await response.json();
    } catch (error) {
      console.error('Failed to load asset data:', error);
    }
  }

  setupTools() {
    // Main tool for getting brand assets
    this.server.setRequestHandler('tools/list', async () => {
      return {
        tools: [
          {
            name: 'get_brand_asset',
            description: 'Get CIQ brand assets with intelligent recommendations based on design context',
            inputSchema: {
              type: 'object',
              properties: {
                request: {
                  type: 'string',
                  description: 'What kind of logo or brand asset do you need? (e.g., "I need a logo for an email signature")'
                },
                background: {
                  type: 'string',
                  enum: ['light', 'dark'],
                  description: 'What background will this logo be placed on?'
                },
                element_type: {
                  type: 'string', 
                  enum: ['main', 'supporting'],
                  description: 'Is this logo the main element/hero of your design, or a supporting element?'
                },
                design_context: {
                  type: 'string',
                  description: 'What type of design is this for? (e.g., "colorful marketing flyer", "minimal black and white ad", "professional presentation")'
                }
              },
              required: ['request']
            }
          },
          {
            name: 'list_all_assets',
            description: 'List all available CIQ brand assets with descriptions',
            inputSchema: {
              type: 'object',
              properties: {},
              required: []
            }
          }
        ]
      };
    });

    this.server.setRequestHandler('tools/call', async (request) => {
      if (request.params.name === 'get_brand_asset') {
        return this.getBrandAsset(request.params.arguments);
      } else if (request.params.name === 'list_all_assets') {
        return this.listAllAssets();
      }
      
      throw new Error(`Unknown tool: ${request.params.name}`);
    });
  }

  async getBrandAsset(args) {
    if (!this.assetData) {
      await this.loadAssetData();
    }

    const { request, background, element_type, design_context } = args;

    // If we don't have enough info, ask clarifying questions
    if (!background) {
      return {
        content: [
          {
            type: 'text',
            text: `I'd love to help you find the perfect CIQ logo! 

What background will this logo be placed on?
• **Light background** (white, light gray, light colors)
• **Dark background** (black, dark gray, dark colors, dark photos)

This helps me recommend the right color version for proper contrast.`
          }
        ]
      };
    }

    if (!element_type) {
      return {
        content: [
          {
            type: 'text', 
            text: `Great! For ${background} backgrounds, I need to understand the logo's role:

🌟 **Main element** - Logo is the hero/star of your design
   • Homepage headers, business cards, presentation title slides
   • Main branding where the logo IS the focus
   
🏷️ **Supporting element** - Logo is secondary/background element  
   • Footers, watermarks, corner branding
   • Small elements that shouldn't compete with main content

Which describes your use case better?`
          }
        ]
      };
    }

    // Apply our smart decision logic
    let recommendation = this.getSmartRecommendation(background, element_type, design_context);
    
    const asset = this.assetData.logos[recommendation.key];
    
    if (!asset) {
      return {
        content: [
          {
            type: 'text',
            text: 'Sorry, I couldn\'t find the appropriate asset. Please try again or contact the design team.'
          }
        ]
      };
    }

    return {
      content: [
        {
          type: 'text',
          text: `Perfect! Here's your CIQ logo:

🎨 **${asset.description}**

📎 **Download:** ${asset.url}

📋 **Usage Guidelines:**
• ${asset.guidance}
• Keep clear space equal to 1/4 the height of the 'Q' around the logo
• Minimum size: 70px height for digital applications

${recommendation.reasoning ? `\n💡 **Why this recommendation:** ${recommendation.reasoning}` : ''}

Need a different variation? Just ask!`
        }
      ]
    };
  }

  getSmartRecommendation(background, elementType, designContext = '') {
    const context = designContext.toLowerCase();
    
    // Main element = always use 2-color for maximum brand recognition
    if (elementType === 'main') {
      return {
        key: `2color-${background}`,
        reasoning: 'Two-color version provides maximum brand recognition for main design elements'
      };
    }

    // Supporting element logic
    if (elementType === 'supporting') {
      // Check for colorful/busy design indicators
      const colorfulKeywords = ['colorful', 'busy', 'marketing', 'promotional', 'lots of color', 'vibrant'];
      const isColorfulDesign = colorfulKeywords.some(keyword => context.includes(keyword));
      
      if (isColorfulDesign) {
        return {
          key: `1color-${background}`,
          reasoning: 'Neutral version won\'t compete with your colorful design elements'
        };
      }

      // Check for minimal/neutral design indicators  
      const minimalKeywords = ['minimal', 'clean', 'simple', 'black and white', 'neutral', 'advertising', 'ad'];
      const isMinimalDesign = minimalKeywords.some(keyword => context.includes(keyword));
      
      if (isMinimalDesign && (context.includes('ad') || context.includes('advertising'))) {
        return {
          key: `green-${background}`,
          reasoning: 'Green version helps your logo jump out in minimal advertising designs'
        };
      }

      // Default to neutral for supporting elements (when in doubt)
      return {
        key: `1color-${background}`,
        reasoning: 'Neutral version is professional and won\'t distract from your main content'
      };
    }

    // Fallback
    return {
      key: `1color-${background}`,
      reasoning: 'When in doubt, neutral is the safest choice'
    };
  }

  async listAllAssets() {
    if (!this.assetData) {
      await this.loadAssetData();
    }

    const assetList = Object.entries(this.assetData.logos).map(([key, asset]) => {
      return `• **${asset.filename}** - ${asset.description}
  📎 ${asset.url}`;
    }).join('\n\n');

    return {
      content: [
        {
          type: 'text',
          text: `# CIQ Brand Assets Available

${assetList}

## 💡 Smart Recommendations Available
Instead of choosing manually, just tell me what you need! For example:
• "I need a logo for an email signature"
• "Logo for a PowerPoint footer" 
• "Small logo for a magazine ad"
• "Hero logo for our homepage"

I'll ask smart questions and recommend the perfect logo for your specific use case!`
        }
      ]
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('CIQ Brand Assets MCP server running on stdio');
  }
}

const server = new CIQBrandAssetsServer();
server.run().catch(console.error);
