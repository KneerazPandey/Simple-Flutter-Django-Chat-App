import 'package:frontend/user.dart';
import 'package:get/get.dart';

class UserController extends GetxController {
  final Rx<User> _loggedInUser = User(
    id: 0,
    userName: '',
    token: const Token(
      accessToken: '',
      refreshToken: '',
    ),
  ).obs;

  User get loggedInUser {
    return _loggedInUser.value;
  }

  void setLoggedInUser(User user) {
    _loggedInUser.value = user;
  }
}
