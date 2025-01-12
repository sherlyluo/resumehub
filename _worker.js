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
      if (url.pathname === '/' || url.pathname === '/index.html') {
        const response = await fetch('https://raw.githubusercontent.com/sherlyluo/resumehub/main/public/index.html');
        const content = await response.text();
        return new Response(content, {
          headers: { 'Content-Type': 'text/html' },
        });
      }

      if (url.pathname === '/script.js') {
        const response = await fetch('https://raw.githubusercontent.com/sherlyluo/resumehub/main/public/script.js');
        const content = await response.text();
        return new Response(content, {
          headers: { 'Content-Type': 'application/javascript' },
        });
      }

      if (url.pathname === '/styles.css') {
        const response = await fetch('https://raw.githubusercontent.com/sherlyluo/resumehub/main/public/styles.css');
        const content = await response.text();
        return new Response(content, {
          headers: { 'Content-Type': 'text/css' },
        });
      }

      return new Response('Not Found', { status: 404 });
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
