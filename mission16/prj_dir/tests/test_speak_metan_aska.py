# test_speak_metan_aska.py

import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from voicevox_mcp_server.mod_speak_metan_aska import speak_metan_aska


class TestSpeakMetanAska(unittest.TestCase):
    
    @patch('voicevox_mcp_server.mod_speak_metan_aska.sd.play')
    @patch('voicevox_mcp_server.mod_speak_metan_aska.sd.wait')
    @patch('voicevox_mcp_server.mod_speak_metan_aska.requests.post')
    def test_speak_metan_aska_success(self, mock_post, mock_wait, mock_play):
        """正常系：音声合成と再生が正しく行われることを確認"""
        
        # モックの設定
        # audio_queryのレスポンス
        mock_query_response = MagicMock()
        mock_query_response.json.return_value = {"accent_phrases": []}
        
        # synthesisのレスポンス（WAVファイル）
        # 44バイトのWAVヘッダー + 音声データ
        wav_header = b'\x00' * 44
        audio_data = np.array([100, 200, 300], dtype=np.int16).tobytes()
        mock_synthesis_response = MagicMock()
        mock_synthesis_response.content = wav_header + audio_data
        
        # postの戻り値を設定（1回目がquery、2回目がsynthesis）
        mock_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        # 関数実行
        speak_metan_aska("テストメッセージ")
        
        # 検証
        self.assertEqual(mock_post.call_count, 2)
        
        # 1回目の呼び出し（audio_query）
        first_call = mock_post.call_args_list[0]
        self.assertIn('audio_query', first_call[0][0])
        self.assertEqual(first_call[1]['params']['text'], "テストメッセージ")
        self.assertEqual(first_call[1]['params']['speaker'], 6)
        
        # 2回目の呼び出し（synthesis）
        second_call = mock_post.call_args_list[1]
        self.assertIn('synthesis', second_call[0][0])
        self.assertEqual(second_call[1]['params']['speaker'], 6)
        
        # 再生が呼ばれたことを確認
        mock_play.assert_called_once()
        mock_wait.assert_called_once()
        
        # 再生されたデータの検証
        play_args = mock_play.call_args
        self.assertEqual(play_args[1]['samplerate'], 24000)
    
    @patch('voicevox_mcp_server.mod_speak_metan_aska.requests.post')
    def test_speak_metan_aska_query_error(self, mock_post):
        """異常系：audio_query APIがエラーを返す場合"""
        
        # モックの設定：HTTPエラーを発生させる
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_post.return_value = mock_response
        
        # 例外が発生することを確認
        with self.assertRaises(Exception):
            speak_metan_aska("テストメッセージ")
    
    @patch('voicevox_mcp_server.mod_speak_metan_aska.sd.play')
    @patch('voicevox_mcp_server.mod_speak_metan_aska.requests.post')
    def test_speak_metan_aska_empty_message(self, mock_post, mock_play):
        """境界値テスト：空文字列のメッセージ"""
        
        # モックの設定
        mock_query_response = MagicMock()
        mock_query_response.json.return_value = {"accent_phrases": []}
        
        wav_header = b'\x00' * 44
        audio_data = b''
        mock_synthesis_response = MagicMock()
        mock_synthesis_response.content = wav_header + audio_data
        
        mock_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        # 関数実行（空文字でもエラーにならないことを確認）
        try:
            speak_metan_aska("")
        except Exception as e:
            self.fail(f"Empty message should not raise exception: {e}")


if __name__ == '__main__':
    unittest.main()
    