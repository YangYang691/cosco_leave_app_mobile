import "dart:io";
import "package:flutter/services.dart";
import "package:path/path.dart";
import "package:sqflite/sqflite.dart";

class DBHelper {
  static final DBHelper _instance = DBHelper._internal();
  factory DBHelper() => _instance;
  DBHelper._internal();

  Database? _db;

  Future<Database> get db async {
    if (_db != null) return _db!;
    _db = await _initDb();
    return _db!;
  }

  Future<Database> _initDb() async {
    final databasesPath = await getDatabasesPath();
    final path = join(databasesPath, "user.db");

    final exists = await databaseExists(path);
    if (!exists) {
      try { await Directory(dirname(path)).create(recursive: true); } catch (_) {}
      ByteData data = await rootBundle.load("assets/database/user.db");
      List<int> bytes = data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
      await File(path).writeAsBytes(bytes, flush: true);
    }

    return await openDatabase(path, readOnly: false);
  }
}
