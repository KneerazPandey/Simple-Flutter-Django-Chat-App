class Message {
  final String fromUser;
  final String toUser;
  final String message;

  Message({
    required this.fromUser,
    required this.toUser,
    required this.message,
  });

  factory Message.fromMap(Map<String, dynamic> map) {
    return Message(
      fromUser: map['from_user'] ?? '',
      toUser: map['to_user'] ?? '',
      message: map['content'] ?? '',
    );
  }
}
