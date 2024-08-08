* ファイル
  - network.pyx : Cython 化した python コード， シミュレータ
  - setup.py : network.pyx から Cyhton を使って拡張モジュール network を作る python ソースコード
  - m_network.py : 拡張モジュール network を使って実験を行う python ソースコード
  - position.py : トポロジファイルを読み込み，ユーザ位置を出力する python ソースコード
  - tree.py : 完全二分木ネットワーク(重みなし)の隣接リストの情報を出力する python ソースコード
  - gba.py : GBA ネットワーク(重みなし)の隣接リストの情報を出力する python ソースコード

  - result.pyx : Cython 化した python コード， 平均値の計算
  - m_result.py : 拡張モジュール result を使って平均値の計算を行う python ソースコード 

* 実験前の手順
 - cython のインストール
   $ pip install cython

 - network.pyx から拡張モジュール network の作成

   $ python setup.py build_ext --inplace

   ※ ↑を実行すると，カレントディレクトリに拡張モジュール network のファイルが作成される

  
* 実験の手順
  - tree.py を実行し，トポロジファイルを作成
  ex) python tree.py 63 > tree.tpl
  
  - position.py を実行し，ユーザ位置のファイルを作成
  ex) python position.py 63 4 tree.tpl CC 1 > tree.pos
  
  - m_network.py を実行して，実験を行う
  ex) python m_network.py 63 1 4 8 tree.tpl tree.pos 1 > tree.res

  - m_result.py を実行して，平均値を得る
  ex) python m_result.py 63 tree.tpl tree.pos tree.res 4 8 > res.res
