export default {
  async fetch(request, env, ctx) {
    try {
      const url = new URL(request.url);
      
      // Handle API requests
      if (url.pathname === '/api/contact' && request.method === 'POST') {
        ctx.waitUntil(
          (async () => {
            try {
              const data = await request.clone().json();
              ctx.log.info('Form submission received:', { data });
              
              // Validate required fields
              const requiredFields = ['name', 'email', 'selected_package'];
              for (const field of requiredFields) {
                if (!data[field]) {
                  ctx.log.error(`Missing required field: ${field}`);
                  throw new Error(`${field} is required`);
                }
              }

              // Send email notification using SendGrid
              const emailContent = `
New Contact Form Submission:
--------------------------
Name: ${data.name}
Email: ${data.email}
Phone: ${data.phone || 'Not provided'}
Selected Package: ${data.selected_package}
Message: ${data.message || 'No message provided'}
--------------------------
Submitted at: ${new Date().toISOString()}
`;

              ctx.log.info('Sending email via SendGrid');
              const emailResponse = await fetch('https://api.sendgrid.com/v3/mail/send', {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${env.SENDGRID_API_KEY}`,
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  personalizations: [{
                    to: [{ email: 'xiuxiu.luo@gmail.com', name: 'Xiuxiu Luo' }]
                  }],
                  from: { email: 'noreply@resumehub.com', name: 'ResumeHub Contact Form' },
                  subject: `New Contact Form Submission from ${data.name}`,
                  content: [{
                    type: 'text/plain',
                    value: emailContent
                  }]
                })
              });

              const responseStatus = emailResponse.status;
              ctx.log.info('SendGrid API response status:', { status: responseStatus });

              if (!emailResponse.ok) {
                const errorText = await emailResponse.text();
                ctx.log.error('SendGrid API error:', { 
                  status: responseStatus,
                  response: errorText 
                });
                throw new Error(`SendGrid API error: ${responseStatus}`);
              }

              ctx.log.info('Email sent successfully');

              // Send confirmation email to the user
              const confirmationResponse = await fetch('https://api.sendgrid.com/v3/mail/send', {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${env.SENDGRID_API_KEY}`,
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  personalizations: [{
                    to: [{ email: data.email, name: data.name }]
                  }],
                  from: { email: 'noreply@resumehub.com', name: 'ResumeHub' },
                  subject: 'Thank you for contacting ResumeHub',
                  content: [{
                    type: 'text/plain',
                    value: `Dear ${data.name},

Thank you for contacting ResumeHub! We have received your inquiry about our ${data.selected_package} package.

We will review your submission and get back to you within 24 hours.

Your submission details:
- Package Selected: ${data.selected_package}
- Email: ${data.email}
${data.phone ? `- Phone: ${data.phone}` : ''}
${data.message ? `- Message: ${data.message}` : ''}

Best regards,
The ResumeHub Team`
                  }]
                })
              });

              if (!confirmationResponse.ok) {
                const errorText = await confirmationResponse.text();
                ctx.log.error('Confirmation email error:', {
                  status: confirmationResponse.status,
                  response: errorText
                });
              }

            } catch (error) {
              ctx.log.error('Error processing form:', {
                error: error.message,
                stack: error.stack
              });
            }
          })()
        );

        // Always return success to the client
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
      ctx.log.error('Unhandled error:', {
        error: error.message,
        stack: error.stack
      });
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
