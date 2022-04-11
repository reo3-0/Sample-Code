# Static geospatial plotting using freshwater salinity and economic data 
#
# Code originally used in research paper titled:
# "Investigating Freshwater Salinity and Economic Development"

def world_pd_2_world_geo(df_final):
    # Takes a pandas df, merges with naturalearth_lowres, returns a geopandas df.
    world_geo = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world_geo['name'] = world_geo['name'].apply(lambda x : reconcile_world_country_names(x, df_final))
    df_merged_pandas = df_final.merge(world_geo[['name', 'geometry']], left_on='Country', right_on='name')
    df_merged_geo = geopandas.GeoDataFrame(df_merged_pandas, geometry='geometry')
    df_merged_geo.set_crs(epsg=4326) # Hardcode, not a clear way to extract
    return df_merged_geo

def plot_grand_summary_world_map(df_final, summary_var, save_title=False):
    df_final_geo = world_pd_2_world_geo(df_final)
    df_grand_total = df_final_geo.groupby('Country').aggregate(geometry=('geometry','first'),
                                                               Count=('Count','sum'),
                                                               Avg_EC=('Avg_EC','mean'),
                                                               Avg_Ann_Station_Count=('Stat_ID_Count', 'mean'))
    fig_total, ax_total = plt.subplots(figsize=(7,7))
    divider = make_axes_locatable(ax_total) 
    cax = divider.append_axes('right', size='5%', pad=0.1) # To adjust map scale
    ax_total = df_grand_total.plot(ax=ax_total, column=summary_var,
                                   edgecolor='grey', legend=True,
                                   cmap='Spectral', cax=cax)
    ax_total.set_title(f'Total {summary_var} Across All Data and Years', weight='bold')
    if(save_title):
        fig_total.savefig(os.path.join(path,f'{save_title}.png'))

def plot_2_by_2_choropleth(df_final, year, var_list, save_title=False):
    colors = ['PuRd_r', 'cividis', 'YlOrBr_r', 'RdBu']
    face_color = 'lightsteelblue'
    color_map_dict = dict(zip(var_list, colors))
    df_final_geo = world_pd_2_world_geo(df_final)
    this_df = df_final_geo[df_final_geo['Year'] == year]
    fig_chlor, ax_chlor = plt.subplots(2,2,figsize=(10,5), constrained_layout=True)
    fig_chlor.tight_layout(pad=0.5)
    fig_chlor.set_facecolor(face_color)
    axs_flat = [ax for sublist in ax_chlor for ax in sublist]
    for this_ax, var in zip(axs_flat, var_list):
        divider = make_axes_locatable(this_ax)
        cax = divider.append_axes('right', size='5%', pad=0.1)
        this_ax = this_df.plot(ax=this_ax, column=var,
                               edgecolor='black', legend=True,
                               cmap=color_map_dict[var], cax=cax)
        var_title = var.replace('_',' ')
        this_ax.set_title(f'{var_title} in {year}', weight='bold')
        this_ax.set_facecolor(face_color)
    if(save_title):
        fig_chlor.savefig(os.path.join(path, f'{save_title}.png'), bbox_inches='tight')
