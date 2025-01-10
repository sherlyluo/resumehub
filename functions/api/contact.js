export async function onRequestPost(context) {
  try {
    const data = await context.request.json();
    
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
    await context.env.CONTACTS.put(contactId, JSON.stringify({
      ...data,
      created_at: new Date().toISOString()
    }));

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

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
