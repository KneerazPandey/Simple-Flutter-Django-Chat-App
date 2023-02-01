import 'dart:convert';
import 'dart:developer';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_stream_listener/flutter_stream_listener.dart';
import 'package:frontend/controller.dart';
import 'package:frontend/message.dart';
import 'package:http/http.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class Chatpage extends StatefulWidget {
  final String userName;

  const Chatpage({
    Key? key,
    required this.userName,
  }) : super(key: key);

  @override
  State<Chatpage> createState() => _ChatpageState();
}

class _ChatpageState extends State<Chatpage> {
  late WebSocketChannel _channel;
  final TextEditingController _messageController = TextEditingController();
  List<Message> _messages = [];
  bool _isTyping = false;
  String _typingMessage = '';

  @override
  void initState() {
    super.initState();
    _channel = WebSocketChannel.connect(
      kIsWeb
          ? Uri.parse(
              'ws://127.0.0.1:8000/${getConversationName(widget.userName)}/?token=${userController.loggedInUser.token.accessToken}')
          : Uri.parse(
              'ws://10.0.2.2:8000/${getConversationName(widget.userName)}/?token=${userController.loggedInUser.token.accessToken}'),
    );

    _messageController.addListener(() {});

    getHistoryMessages();
  }

  @override
  void dispose() {
    _channel.sink.close();
    _messageController.dispose();
    super.dispose();
  }

  void getHistoryMessages() async {
    Uri uri = Uri.parse(kIsWeb
        ? 'http://127.0.0.1:8000/chats/${widget.userName}'
        : 'http://10.0.2.2:8000/chats/${widget.userName}');
    Response response = await get(
      uri,
      headers: {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization':
            'Bearer ${userController.loggedInUser.token.accessToken}',
      },
    );
    log(response.statusCode.toString());
    if (response.statusCode == 200) {
      List<Message> messages = [];
      List<dynamic> datas = jsonDecode(response.body);
      log(datas.toString());
      for (var data in datas) {
        Message message = Message.fromMap(data);
        messages.add(message);
      }
      log(messages.toString());
      setState(() {
        _messages = messages;
      });
    }
  }

  static String getConversationName(String userName) {
    List<String> names = [userController.loggedInUser.userName, userName];
    names.sort();
    return "${names[0]}_${names[1]}";
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        FocusScope.of(context).unfocus();
        _channel.sink.add(jsonEncode({
          'type': 'stop_typing',
        }));
      },
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.userName),
          centerTitle: true,
          backgroundColor: Colors.red,
        ),
        body: StreamListener(
          stream: _channel.stream,
          onData: (data) {
            if (data != null) {
              Map<String, dynamic> content = jsonDecode(data.toString());
              String type = content['type'];
              switch (type) {
                case "chat_message":
                  Message message = Message.fromMap(content);
                  _messages.add(message);
                  setState(() {});
                  break;
                case "typing":
                  String typingUsername = content['user'];
                  if (typingUsername != userController.loggedInUser.userName) {
                    setState(() {
                      _isTyping = true;
                      _typingMessage = content['message'];
                    });
                  }
                  break;
                case "stop_typing":
                  setState(() {
                    _isTyping = false;
                    _typingMessage = '';
                  });
                  break;
                default:
                  break;
              }
            }
          },
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Column(
              children: [
                const SizedBox(height: 15),
                Expanded(
                  child: ListView.builder(
                      itemCount: _messages.length,
                      itemBuilder: (BuildContext context, int index) {
                        Message message = _messages[index];
                        return Row(
                          mainAxisSize: MainAxisSize.max,
                          mainAxisAlignment: message.fromUser ==
                                  userController.loggedInUser.userName
                              ? MainAxisAlignment.end
                              : MainAxisAlignment.start,
                          children: [
                            Text(
                              message.message,
                            ),
                          ],
                        );
                      }),
                ),
                TextField(
                  controller: _messageController,
                  decoration: const InputDecoration(
                    border: OutlineInputBorder(),
                    hintText: 'Enter your message',
                  ),
                  onChanged: (String data) {
                    _channel.sink.add(jsonEncode({
                      'type': 'typing',
                    }));
                  },
                  onEditingComplete: () {
                    _channel.sink.add(jsonEncode({
                      'type': 'stop_typing',
                    }));
                  },
                  onSubmitted: (data) {
                    _channel.sink.add(jsonEncode({
                      'type': 'stop_typing',
                    }));
                  },
                ),
                const SizedBox(height: 20),
                if (_isTyping) Text(_typingMessage),
                const SizedBox(height: 10),
                ElevatedButton(
                  onPressed: () {
                    if (_messageController.text.isNotEmpty) {
                      _channel.sink.add(jsonEncode({
                        'type': 'chat_message',
                        'message': _messageController.text,
                        'from_user': userController.loggedInUser.userName,
                        'to_user': widget.userName,
                      }));
                      _messageController.text = "";
                    }
                  },
                  child: const Text('Send Message'),
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
