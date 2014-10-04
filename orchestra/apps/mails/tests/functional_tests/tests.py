#import imaplib
#mail = imaplib.IMAP4_SSL('localhost')
#mail.login('rata', '3')
#('OK', ['Logged in'])

#>>> mail.list()
#('OK', ['(\\HasNoChildren) "." INBOX'])
#>>> mail.select('INBOX')
#('OK', ['18'])

#>>> mail.getquota('INBOX')
#imaplib.error: GETQUOTA command error: BAD ['Error in IMAP command GETQUOTA: Unknown command.']

#mail.fetch(10, '(RFC822)')
#('OK', [('10 (FLAGS (\\Seen) RFC822 {550}', 'Return-Path: <root@test3.orchestra.lan>\r\nDelivered-To: <rata@orchestra.lan>\r\nReceived: from test3.orchestra.lan\r\n\tby test3.orchestra.lan (Dovecot) with LMTP id hvDUEAIKL1QlOQAAL4hJug\r\n\tfor <rata@orchestra.lan>; Fri, 03 Oct 2014 16:41:38 -0400\r\nReceived: by test3.orchestra.lan (Postfix, from userid 0)\r\n\tid 43BB1F94633; Fri,  3 Oct 2014 16:41:38 -0400 (EDT)\r\nTo: rata@orchestra.lan\r\nSubject: hola\r\nMessage-Id: <20141003204138.43BB1F94633@test3.orchestra.lan>\r\nDate: Fri,  3 Oct 2014 16:41:38 -0400 (EDT)\r\nFrom: root@test3.orchestra.lan (root)\r\n\r\n\r\n\r\n'), ')'])
#>>> mail.close()
#('OK', ['Close completed.'])


#import poplib
#pop = poplib.POP3('localhost')
#pop.user('rata')
#pop.pass_('3')
#>>> pop.list()
#('+OK 18 messages:', ['1 552', '2 550', '3 550', '4 548', '5 546', '6 546', '7 554', '8 548', '9 550', '10 550', '11 546', '12 546', '13 546', '14 544', '15 548', '16 577', '17 546', '18 546'], 135)
#>>> pop.quit()
#'+OK Logging out.'

