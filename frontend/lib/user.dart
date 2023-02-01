class User {
  final int id;
  final String userName;
  final Token token;

  User({
    required this.id,
    required this.userName,
    required this.token,
  });

  factory User.fromMap(Map<String, dynamic> map) {
    return User(
      id: (map['id'] as num).toInt(),
      userName: map['username'] ?? '',
      token: Token.fromMap(map['tokens'] ?? {}),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'username': userName,
      'token': token,
    };
  }
}

class Token {
  final String accessToken;
  final String refreshToken;

  const Token({
    required this.accessToken,
    required this.refreshToken,
  });

  factory Token.fromMap(Map<String, dynamic> map) {
    return Token(
      accessToken: map['access_token'] ?? '',
      refreshToken: map['refresh_token'] ?? '',
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
    };
  }
}
