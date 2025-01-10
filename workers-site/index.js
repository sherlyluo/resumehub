import { getAssetFromKV } from '@cloudflare/kv-asset-handler';

// Configure environment variables in Cloudflare Workers
const CONTACT_NAMESPACE = 'CONTACTS';

async function handleApiRequest(request) {
  if (request.method === 'POST' && new URL(request.url).pathname === '/api/contact') {
    try {
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

      // Generate unique ID for the contact
      const contactId = Date.now().toString();
      
      // Store contact in KV
      await CONTACTS.put(contactId, JSON.stringify({
        ...data,
        created_at: new Date().toISOString()
      }));

      // Send email notification using Cloudflare Email Workers (if configured)
      if (typeof EMAIL_SERVICE !== 'undefined') {
        await EMAIL_SERVICE.send({
          to: data.email,
          from: 'noreply@your-domain.com',
          subject: 'Thank you for your interest',
          text: `Dear ${data.name},\n\nThank you for your interest in our services. We will contact you shortly.\n\nBest regards,\nYour Team`
        });
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
    } catch (err) {
      console.error('Error processing contact form:', err);
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

  // Handle CORS preflight requests
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  }

  return null;
}

async function handleEvent(event) {
  try {
    // Check if it's an API request
    const apiResponse = await handleApiRequest(event.request);
    if (apiResponse) return apiResponse;

    // Otherwise, serve static assets
    return await getAssetFromKV(event);
  } catch (err) {
    console.error('Error handling request:', err);
    return new Response('Internal Error', { status: 500 });
  }
}

addEventListener('fetch', event => {
  event.respondWith(handleEvent(event));
});
