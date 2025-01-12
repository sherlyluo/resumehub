export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      
      // Handle API requests
      if (url.pathname === '/api/contact' && request.method === 'POST') {
        const data = await request.json();
        
        // Validate required fields
        const requiredFields = ['name', 'email', 'selected_package'];
        for (const field of requiredFields) {
          if (!data[field]) {
            return new Response(
              JSON.stringify({ error: `${field} is required` }),
              { 
                status: 400,
                headers: {
                  'Content-Type': 'application/json',
                  'Access-Control-Allow-Origin': '*'
                }
              }
            );
          }
        }

        return new Response(
          JSON.stringify({ message: 'Contact form submitted successfully' }),
          { 
            status: 200,
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*'
            }
          }
        );
      }

      // Handle CORS preflight
      if (request.method === 'OPTIONS') {
        return new Response(null, {
          headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
          }
        });
      }

      // Serve static files
      return env.ASSETS.fetch(request);
      
    } catch (error) {
      return new Response(
        JSON.stringify({ error: 'Internal server error' }),
        { 
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        }
      );
    }
  }
};
