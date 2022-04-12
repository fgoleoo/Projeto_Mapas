import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy
import numpy as np
import pandas as pd
import datetime
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER

###########################################VARIAVEIS GLOBAIS############################################################

path = r'H:\Comercializadora\Preços\Leonardo\Projetos_Python\Projeto_Mapas'

path_rodada00 = r'\GFS_T00'
path_rodada12 = r'\GFS_T12'

path_to_save1 = r'H:\Comercializadora\Preços\Leonardo\Projetos_Python\Projeto_Mapas\pentada_1_' + datetime.datetime.now().strftime(
    "%d_%m_%y")
path_to_save2 = r'H:\Comercializadora\Preços\Leonardo\Projetos_Python\Projeto_Mapas\pentada_2_' + datetime.datetime.now().strftime(
    "%d_%m_%y")
path_to_save3 = r'H:\Comercializadora\Preços\Leonardo\Projetos_Python\Projeto_Mapas\pentada_3_' + datetime.datetime.now().strftime(
    "%d_%m_%y")

###############NIVEIS DE CHUVA QUE ESTARÃO NO CBAR######################################################################
levels = (-100, -75, -50, -25, -10, -5, -2.5, 2.5, 5, 10, 25, 50, 75, 100)


############## no main para usar a mesma função, pentada vai ter q assumir 3 valores (0,5 e 10)


def main():
    df_pentada_1_00Z = acumula_pentadas(path, path_rodada00, 0)
    df_pentada_2_00Z = acumula_pentadas(path, path_rodada00, 5)
    df_pentada_3_00Z = acumula_pentadas(path, path_rodada00, 10)

    df_pentada_1_12Z = acumula_pentadas(path, path_rodada12, 0)
    df_pentada_2_12Z = acumula_pentadas(path, path_rodada12, 5)
    df_pentada_3_12Z = acumula_pentadas(path, path_rodada12, 10)

    map_dif(df_pentada_1_00Z, df_pentada_1_12Z, path_to_save1, 1)
    map_dif(df_pentada_2_00Z, df_pentada_2_12Z, path_to_save2, 2)
    map_dif(df_pentada_3_00Z, df_pentada_3_12Z, path_to_save3, 3)


# funcao que faz os acumulados em pentadas
def acumula_pentadas(path, path_rodada00, pentada):
    dia_previsao = datetime.datetime.now().strftime("%d%m%y")

    lista_de_caminhos = []
    for contador in range(1, 6):
        i = contador + pentada
        lista_de_caminhos.append(
            "\GFS_p" + dia_previsao + "a" + (datetime.datetime.now() + datetime.timedelta(days=i)).strftime(
                "%d%m%y") + ".dat")

    df_merge = pd.read_fwf(path + path_rodada00 + lista_de_caminhos[0], header=None, widths=[7, 7, 10],
                           names=["longitude", "latitude", "acumulado"])
    for caminho in lista_de_caminhos[1:]:
        df_lido = pd.read_fwf(path + path_rodada00 + caminho, header=None, widths=[7, 7, 10],
                              names=["longitude", "latitude", "acumulado" + caminho])
        df_merge = df_merge.merge(df_lido, how='left')

    df_merge['somatorio_acumulado'] = df_merge.loc[:, 'acumulado':].sum(axis=1)

    return df_merge


# funcao que faz a diferença entre as rodadas e plota o mapa
def map_dif(df_pentada_00Z, df_pentada_12Z, path_to_save, num_pentada):
    x = df_pentada_00Z['longitude'].unique()
    y = df_pentada_00Z['latitude'].unique()
    X, Y = np.meshgrid(x, y)

    df_pivot1 = pd.pivot_table(df_pentada_00Z, values=["somatorio_acumulado"], index=["longitude"],
                               columns=["latitude"], dropna=False)
    df_pivot2 = pd.pivot_table(df_pentada_12Z, values=["somatorio_acumulado"], index=["longitude"],
                               columns=["latitude"], dropna=False)

    df_diferenca = df_pivot2 - df_pivot1

    fig = plt.figure(figsize=(10, 8), dpi=100, frameon=False)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    ax.set_xticks([-75, -65, -55, -45, -35], crs=ccrs.PlateCarree())
    ax.set_yticks([5, 0, -5, -10, -15, -20, -25, -30, -35], crs=ccrs.PlateCarree())
    ax.set_extent([-75, -30.2, -35, 5], crs=ccrs.PlateCarree())
    lon_formatter = LONGITUDE_FORMATTER
    lat_formatter = LATITUDE_FORMATTER
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)

    cs = plt.contourf(X.T, Y.T, df_diferenca.values, cmap='seismic_r', extend='both', alpha=0.90, levels=levels, )

    cbar = plt.colorbar(cs, label='Diferença [mm]', shrink=0.85)
    cbar.set_ticks(levels)
    cbar.ax.tick_params(labelsize=8)
    cbar.ax.set_yticklabels([f'{i:+.1f}'.format(i) for i in cbar.get_ticks()])  # set ticks of your format

    ax.coastlines(resolution='10m')
    ax.add_feature(cartopy.feature.BORDERS)
    ax.add_feature(cartopy.feature.OCEAN, edgecolor='gray', facecolor='gray')

    #  adiciona o shapefile das bacias hidrograficas consideradas pelo ONS
    shp_file = r'H:\Comercializadora\Preços\Leonardo\Projetos_Python\Projeto_Mapas\Contornos\SIN\Contorno_Bacias_rev2.shp'
    shape_feature = ShapelyFeature(Reader(shp_file).geometries(), ccrs.PlateCarree(), edgecolor='gray',
                                   facecolor='none', lw=0.75)
    ax.add_feature(shape_feature)

    plt.title(label="Dif. entre as rodadas (12Z-00Z) GFS  --  " + datetime.datetime.now().strftime(
        "%d/%m/%y") + "  --  " + str(num_pentada) + "ª Pêntada", y=1.02)

    fig.savefig(path_to_save, dpi=fig.dpi, bbox_inches='tight')
    plt.close()

    return None


if __name__ == '__main__':
    main()
