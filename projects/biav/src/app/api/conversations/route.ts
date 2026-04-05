import { NextRequest, NextResponse } from 'next/server'
import { listConversations, deleteConversation, updateConversationTitle } from '@/lib/db'

export async function GET() {
  const conversations = listConversations()
  return NextResponse.json(conversations)
}

export async function DELETE(req: NextRequest) {
  try {
    const { id } = await req.json()
    if (id) deleteConversation(id)
    return NextResponse.json({ ok: true })
  } catch {
    return NextResponse.json({ error: 'Invalid request body' }, { status: 400 })
  }
}

export async function PATCH(req: NextRequest) {
  try {
    const { id, title } = await req.json()
    if (id && title) updateConversationTitle(id, title)
    return NextResponse.json({ ok: true })
  } catch {
    return NextResponse.json({ error: 'Invalid request body' }, { status: 400 })
  }
}
