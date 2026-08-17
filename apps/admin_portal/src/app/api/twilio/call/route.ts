import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { to, twimlUrl } = await request.json();
    
    if (!to || !twimlUrl) {
      return NextResponse.json({ error: 'Missing required fields (to, twimlUrl)' }, { status: 400 });
    }

    const accountSid = process.env.TWILIO_ACCOUNT_SID;
    const authToken = process.env.TWILIO_AUTH_TOKEN;
    const fromNumber = process.env.TWILIO_FROM_NUMBER;

    if (!accountSid || !authToken || !fromNumber) {
      return NextResponse.json({ error: 'Twilio credentials not configured in .env' }, { status: 500 });
    }

    const formData = new URLSearchParams();
    formData.append('To', to);
    formData.append('From', fromNumber);
    formData.append('Url', twimlUrl);

    const twilioUrl = `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Calls.json`;

    const response = await fetch(twilioUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': `Basic ${Buffer.from(`${accountSid}:${authToken}`).toString('base64')}`
      },
      body: formData.toString()
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json({ error: data.message || 'Failed to trigger Twilio call' }, { status: response.status });
    }

    return NextResponse.json({ success: true, sid: data.sid });
  } catch (error: any) {
    console.error('Twilio Error:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
